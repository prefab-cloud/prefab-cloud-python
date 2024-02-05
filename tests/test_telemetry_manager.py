import prefab_pb2 as Prefab
from prefab_cloud_python import Options, Client
from prefab_cloud_python._telemetry import TelemetryManager
from prefab_cloud_python.config_resolver import Evaluation
from prefab_cloud_python.context import Context
import pytest
import responses

from tests.helpers import EmptyResolver, sort_proto_evaluation_counters


TIMEVAL = 1234567890.0
TIMEVAL2 = 1234567899.0
EMPTY_CONTEXT = Context()
EMPTY_RESOLVER = EmptyResolver()

CONFIG1 = Prefab.Config(key="key1", config_type="CONFIG", id=1001, rows=[])

CONFIG2 = Prefab.Config(key="key2", config_type="CONFIG", id=1002, rows=[])

VALUE1 = Prefab.ConfigValue(int=100)
VALUE2 = Prefab.ConfigValue(int=200)


@pytest.fixture(autouse=True)
def responses_fixture(monkeypatch):
    responses.start()
    responses.add(
        responses.POST,
        url="http://api.staging-prefab.cloud/api/v1/telemetry/",
        status=200,
    )
    yield
    responses.stop()
    responses.reset()


@pytest.fixture
def client() -> Client:
    options = Options(
        collect_evaluation_summaries=True,
        collect_sync_interval=0,
        prefab_datasources="LOCAL_ONLY",
    )
    options.prefab_api_url = "http://api.staging-prefab.cloud"
    return Client(options)


@pytest.fixture
def telemetry_manager(client: Client) -> TelemetryManager:
    telemetry_manager = TelemetryManager(client)
    yield telemetry_manager
    telemetry_manager.stop()


def test_evaluation_summary_telemetry(telemetry_manager: TelemetryManager):
    telemetry_manager.record_evaluation(
        Evaluation(
            config=CONFIG1,
            value=VALUE1,
            value_index=31,
            config_row_index=0,
            resolver=EMPTY_RESOLVER,
            context=EMPTY_CONTEXT,
        )
    )
    telemetry_manager.record_evaluation(
        Evaluation(
            config=CONFIG1,
            value=VALUE2,
            value_index=32,
            config_row_index=0,
            resolver=EMPTY_RESOLVER,
            context=EMPTY_CONTEXT,
        )
    )
    telemetry_manager.flush_and_block()
    assert (
        responses.assert_call_count(
            "http://api.staging-prefab.cloud/api/v1/telemetry/", 1
        )
        is True
    )
    uploaded_telemetry = Prefab.TelemetryEvents()
    uploaded_telemetry.ParseFromString(responses.calls[0].request.body)
    assert len(uploaded_telemetry.events) == 1
    assert len(uploaded_telemetry.events[0].summaries.summaries) == 1
    assert uploaded_telemetry.events[0].summaries.summaries[0].key == CONFIG1.key
    assert sort_proto_evaluation_counters(
        uploaded_telemetry.events[0].summaries.summaries[0].counters
    ) == sort_proto_evaluation_counters(
        [
            Prefab.ConfigEvaluationCounter(
                count=1,
                config_id=CONFIG1.id,
                config_row_index=0,
                conditional_value_index=31,
                selected_value=VALUE1,
            ),
            Prefab.ConfigEvaluationCounter(
                count=1,
                config_id=CONFIG1.id,
                config_row_index=0,
                conditional_value_index=32,
                selected_value=VALUE2,
            ),
        ]
    )
