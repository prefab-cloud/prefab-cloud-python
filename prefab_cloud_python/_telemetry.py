import threading
from queue import Queue, Full
import time
from enum import Enum
from abc import ABC

from prefab_pb2 import (
    ConfigEvaluationSummary,
    ConfigEvaluationSummaries,
    ConfigEvaluationCounter,
    TelemetryEvent,
    TelemetryEvents,
)
from .config_resolver import Evaluation
from collections import defaultdict


def current_time_millis() -> int:
    return int(time.time() * 1000)


class BaseTelemetryEvent(ABC):
    class Type(Enum):
        EVAL = 1
        FLUSH = 2

    def __init__(self, event_type=Type.FLUSH, timestamp=None):
        self.event_type = event_type
        self.timestamp = timestamp if timestamp is not None else current_time_millis()


class FlushTelemetryEvent(BaseTelemetryEvent):
    def __init__(self):
        super().__init__(event_type=BaseTelemetryEvent.Type.FLUSH)
        self.processed_event = threading.Event()

    def block_until_consumed(self):
        self.processed_event.wait()

    def mark_finished(self):
        self.processed_event.set()


class EvaluationTelemetryEvent(BaseTelemetryEvent):
    def __init__(self, evaluation: Evaluation):
        super().__init__(event_type=BaseTelemetryEvent.Type.EVAL)
        self.evaluation = evaluation


class TelemetryManager(object):
    def __init__(self, client) -> None:
        self.client = client
        self.report_interval = client.options.collect_sync_interval
        self.report_summaries = client.options.collect_evaluation_summaries
        self.sync_started = False
        self.event_processor = TelemetryEventProcessor(
            evaluation_event_handler=self._handle_evaluation,
            flush_event_handler=self._handle_flush,
        )
        self.event_processor.start()
        self.timer = None
        self.evaluation_rollup = EvaluationRollup()

    def start_periodic_sync(self) -> None:
        if self.report_interval:
            self.sync_started = True
            self.timer = threading.Timer(self.report_interval, self.run_sync)
            self.timer.start()

    def stop(self):
        self.sync_started = False

    def run_sync(self) -> None:
        try:
            self.flush()
        finally:
            if self.sync_started:
                self.timer = threading.Timer(self.report_interval, self.run_sync)
                self.timer.start()

    def record_evaluation(self, evaluation: Evaluation) -> None:
        self.event_processor.enqueue(EvaluationTelemetryEvent(evaluation))

    def flush(self) -> FlushTelemetryEvent:
        flush_event = FlushTelemetryEvent()
        self.event_processor.enqueue(flush_event)
        return flush_event

    def flush_and_block(self):
        self.flush().block_until_consumed()

    def _handle_evaluation(self, evaluationEvent: EvaluationTelemetryEvent) -> None:
        if self.report_summaries:
            self.evaluation_rollup.record_evaluation(evaluationEvent.evaluation)

    def _handle_flush(self, flushEvent: FlushTelemetryEvent) -> None:
        try:
            if self.report_summaries:
                current_eval_rollup = self.evaluation_rollup
                eval_summaries = current_eval_rollup.build_telemetry()
                self.evaluation_rollup = EvaluationRollup()

                # TODO retry/log
                self.client.post(
                    "/api/v1/telemetry/",
                    TelemetryEvents(events=[TelemetryEvent(summaries=eval_summaries)]),
                )
        finally:
            flushEvent.mark_finished()


class HashableProtobufWrapper:
    def __init__(self, msg):
        self.msg = msg

    def __hash__(self):
        return hash(self.msg.SerializeToString())

    def __eq__(self, other):
        return self.msg.SerializeToString() == other.msg.SerializeToString()


class EvaluationRollup(object):
    def __init__(self):
        self.counts = defaultdict(lambda: 0)
        self.recorded_since = current_time_millis()

    def record_evaluation(self, evaluation: Evaluation) -> None:
        self.counts[
            (
                evaluation.config.key,
                evaluation.config.config_type,
                evaluation.config.id,
                evaluation.config_row_index,
                evaluation.value_index,
                evaluation.deepest_value().weighted_value_index,
                HashableProtobufWrapper(
                    evaluation.deepest_value().reportable_wrapped_value().value
                ),
            )
        ] += 1

    def build_telemetry(self):
        all_summaries = []
        key_groups = self._get_keys_grouped_by_key_and_type()
        for key_and_type, all_keys in key_groups.items():
            current_counters = []
            for current_key_tuple in all_keys:
                current_counters.append(
                    ConfigEvaluationCounter(
                        count=self.counts[current_key_tuple],
                        config_id=current_key_tuple[2],
                        config_row_index=current_key_tuple[3],
                        conditional_value_index=current_key_tuple[4],
                        weighted_value_index=current_key_tuple[5],
                        selected_value=current_key_tuple[6].msg,
                    )
                )
            all_summaries.append(
                ConfigEvaluationSummary(
                    key=key_and_type[0], type=key_and_type[1], counters=current_counters
                )
            )
        return ConfigEvaluationSummaries(
            start=self.recorded_since,
            end=current_time_millis(),
            summaries=all_summaries,
        )

    def _get_keys_grouped_by_key_and_type(self):
        grouped_keys = defaultdict(list)
        for key in self.counts.keys():
            grouped_keys[(key[0], key[1])].append(key)
        return grouped_keys


class TelemetryEventProcessor(object):
    def __init__(self, evaluation_event_handler=None, flush_event_handler=None) -> None:
        self.thread = None
        self.queue = Queue(10000)
        self.evaluation_event_handler = evaluation_event_handler
        self.flush_event_handler = flush_event_handler

    def start(self) -> None:
        self.thread = threading.Thread(target=self.process_queue, daemon=True)
        self.thread.start()

    def enqueue(self, event: BaseTelemetryEvent):
        try:
            self.queue.put_nowait(event)
        except Full:
            pass

    def process_queue(self):
        while True:
            event = self.queue.get()
            try:
                if (
                    event.event_type == BaseTelemetryEvent.Type.EVAL
                    and self.evaluation_event_handler
                ):
                    self.evaluation_event_handler(event)
                elif (
                    event.event_type == BaseTelemetryEvent.Type.FLUSH
                    and self.flush_event_handler
                ):
                    self.flush_event_handler(event)
                else:
                    raise ValueError(f"Unknown event type: {event.event_type}")

            finally:
                self.queue.task_done()
