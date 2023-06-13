from prefab_cloud_python import Options, Client
import prefab_pb2 as Prefab

import time
import timecop


class TestLogPathAggregator:
    def test_sync(self):
        with timecop.freeze(time.time()):
            options = Options(
                prefab_datasources="ALL",
                api_key="123-development-yourapikey-SDK",
                collect_sync_interval=1000,
                prefab_envs=["unit_tests"],
                prefab_config_classpath_dir="tests",
                namespace="this.is.a.namespace",
                connection_timeout_seconds=0,
                log_boundary="..",
            )
            client = Client(options)

            for _ in range(2):
                client.logger.info("here is a message")
            for _ in range(3):
                client.logger.error("here is a message")

            requests = []

            def new_post(self, *params):
                requests.extend(params)

            funcType = type(client.post)

            client.post = funcType(new_post, client)

            client.log_path_aggregator.sync()

            assert requests == [
                "/api/v1/known-loggers",
                Prefab.Loggers(
                    loggers=[
                        Prefab.Logger(
                            logger_name="prefab_cloud_python.tests.test_log_path_aggregator.test_sync",
                            infos=2,
                            errors=3,
                        )
                    ],
                    start_at=round(time.time() * 1000),
                    end_at=round(time.time() * 1000),
                    instance_hash=client.instance_hash,
                    namespace="this.is.a.namespace",
                ),
            ]
