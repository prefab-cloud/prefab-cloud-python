import logging

from .config_loader import ConfigLoader
from .config_resolver import ConfigResolver
from .read_write_lock import ReadWriteLock
from .config_value_unwrapper import ConfigValueUnwrapper
from .context import Context

import grpc
import threading
import time
import requests
import sseclient
import base64
import prefab_pb2 as Prefab
import functools

logger = logging.getLogger()


class InitializationTimeoutException(Exception):
    def __init__(self, timeout_seconds, key):
        super().__init__(
            f"Prfeab couldn't initialize in {timeout_seconds} second timeout. Trying to fetch key `{key}`."
        )


class MissingDefaultException(Exception):
    def __init__(self, key):
        super().__init__(
            f"""No value found for key '{key}' and no default was provided.

If you'd prefer returning `None` rather than raising when this occurs, modify the `on_no_default` value you provide in your Options."""
        )


class ConfigClient:
    def __init__(self, base_client, timeout):
        logger.info("Initializing ConfigClient")
        self.base_client = base_client
        self.options = base_client.options
        self.timeout = timeout

        self.stream_lock = ReadWriteLock()
        self.init_lock = ReadWriteLock()

        self.checkpoint_freq_secs = 60

        self.config_loader = ConfigLoader(base_client)
        self.config_resolver = ConfigResolver(base_client, self.config_loader)

        logger.debug("Initialize ConfigClient: acquire write lock")
        self.init_lock.acquire_write()
        logger.debug("Initialize ConfigClient: acquired write lock")

        if self.options.is_local_only():
            self.finish_init("local only")
        else:
            self.load_checkpoint()
            self.start_checkpointing_thread()
            self.start_streaming()

    def get(self, key, default="NO_DEFAULT_PROVIDED", context=Context.get_current()):
        value = self.__get(key, None, {}, context=context)

        if isinstance(context, Context):
            self.base_client.context_shape_aggregator.push(context)
        elif not isinstance(context, str):
            self.base_client.context_shape_aggregator.push(Context(context))

        if value is not None:
            return ConfigValueUnwrapper.unwrap(value, key, context)
        else:
            return self.handle_default(key, default)

    def __get(self, key, lookup_key, properties, context=Context.get_current()):
        try:
            self.init_lock.acquire_read(self.options.connection_timeout_seconds)
        except Exception:
            if self.options.on_connection_failure == "RAISE":
                raise InitializationTimeoutException(
                    self.options.connection_timeout_seconds, key
                )
            logger.warn(
                f"Couldn't initialize in {self.options.connection_timeout_seconds}. Key {key}. Returning what we have."
            )
            self.init_lock.release_write()
        finally:
            return self.config_resolver.get(key, context=context)

    def handle_default(self, key, default):
        if default != "NO_DEFAULT_PROVIDED":
            return default
        if self.options.on_no_default == "RAISE":
            raise MissingDefaultException(key)
        return None

    def load_checkpoint(self):
        if self.load_checkpoint_from_api_cdn():
            return
        logger.warning("No success loading checkpoints")

    def start_checkpointing_thread(self):
        self.checkpointing_thread = threading.Thread(target=self.checkpointing_loop)
        self.checkpointing_thread.daemon = True
        self.checkpointing_thread.start()

    def start_streaming(self):
        self.streaming_thread = threading.Thread(target=self.streaming_loop)
        self.streaming_thread.daemon = True
        self.streaming_thread.start()

    def streaming_loop(self):
        url = "%s/api/v1/sse/config" % self.options.prefab_api_url
        auth = "%s:%s" % ("authuser", self.options.api_key)
        token = base64.b64encode(auth.encode("utf-8")).decode("ascii")
        headers = {
            "x-prefab-start-at-id": f"{self.config_loader.highwater_mark}",
            "Authorization": "Basic %s" % token,
        }
        response = self.base_client.session.get(url, headers=headers, stream=True)

        client = sseclient.SSEClient(response)

        for event in client.events():
            if event.data:
                logger.info("Loading data from SSE stream")
                configs = Prefab.Configs.FromString(base64.b64decode(event.data))
                self.load_configs(configs, "sse_streaming")

    def checkpointing_loop(self):
        while True:
            try:
                self.load_checkpoint()
                time.sleep(self.checkpoint_freq_secs)
            except Exception:
                logger.info("Issue Checkpointing")

    def load_checkpoint_from_api_cdn(self):
        url = "%s/api/v1/configs/0" % self.options.url_for_api_cdn
        auth = "%s:%s" % ("authuser", self.options.api_key)
        token = base64.b64encode(auth.encode("utf-8")).decode("ascii")
        headers = {"Authorization": "Basic %s" % token}
        response = requests.get(url, headers=headers)
        if response.ok:
            configs = Prefab.Configs.FromString(response.content)
            self.load_configs(configs, "remote_api_cdn")
            return True
        else:
            logger.info(
                f"Checkpoint remote_cdn_api failed to load. Response {response.status_code}",
            )
            return False

    def load_configs(self, configs, source):
        project_id = configs.config_service_pointer.project_id
        project_env_id = configs.config_service_pointer.project_env_id
        self.config_resolver.project_env_id = project_env_id
        starting_highwater_mark = self.config_loader.highwater_mark
        for config in configs.configs:
            self.config_loader.set(config, source)
        if self.config_loader.highwater_mark > starting_highwater_mark:
            logger.info(
                f"Found new checkpoint with highwater id {self.config_loader.highwater_mark} from {source} in project {project_id} environment: {project_env_id} and namespace {self.base_client.options.namespace}"
            )
        else:
            logger.debug(
                f"Checkpoint with highwater id {self.config_loader.highwater_mark} from {source}. No changes."
            )
        self.config_resolver.update()
        self.finish_init(source)

    def finish_init(self, source):
        if not self.init_lock._write_locked:
            return
        logger.info(f"Unlocked config via {source}")
        self.init_lock.release_write()

    @functools.cache
    def grpc_channel(self):
        creds = grpc.ssl_channel_credentials()
        return grpc.secure_channel(self.options.prefab_grpc_url, creds)
