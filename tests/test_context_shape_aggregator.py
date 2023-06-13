from prefab_cloud_python import Options, Client
from prefab_cloud_python.context import Context
import prefab_pb2 as Prefab

from datetime import date

DOB = date.today()

CONTEXT_1 = Context(
    {
        "user": {"name": "user-name", "email": "user.email", "age": 42.5},
        "subscription": {"plan": "advanced", "free": False},
    }
)

CONTEXT_2 = Context(
    {
        "user": {"name": "other-user-name", "dob": DOB},
        "device": {"name": "device-name", "os": "os-name", "version": 3},
    }
)

CONTEXT_3 = Context({"subscription": {"plan": "pro", "trial": True}})


def new_client(max_shapes=1000):
    options = Options(
        prefab_datasources="ALL",
        api_key="123-development-yourapikey-SDK",
        prefab_envs=["unit_tests"],
        prefab_config_classpath_dir="tests",
        namespace="this.is.a.namespace",
        connection_timeout_seconds=0,
        collect_max_shapes=max_shapes,
        collect_sync_interval=1000,
    )
    return Client(options)


class TestContextShapeAggregator:
    def test_push(self):
        # aggregator = new_aggregator(9)
        client = new_client(max_shapes=9)
        aggregator = client.context_shape_aggregator

        aggregator.push(CONTEXT_1)
        aggregator.push(CONTEXT_2)

        assert len(aggregator.data) == 9

        # we've reached the limit, so no more data added
        aggregator.push(CONTEXT_3)
        assert len(aggregator.data) == 9

        assert aggregator.data == {
            ("user", "name", 2),
            ("user", "email", 2),
            ("user", "age", 4),
            ("subscription", "plan", 2),
            ("subscription", "free", 5),
            ("user", "dob", 2),
            ("device", "name", 2),
            ("device", "os", 2),
            ("device", "version", 1),
        }

    def test_prepare_data(self):
        client = new_client()
        aggregator = client.context_shape_aggregator

        aggregator.push(CONTEXT_1)
        aggregator.push(CONTEXT_2)
        aggregator.push(CONTEXT_3)

        data = aggregator.prepare_data()

        assert data == {
            "user": {"name": 2, "email": 2, "dob": 2, "age": 4},
            "subscription": {"plan": 2, "trial": 5, "free": 5},
            "device": {"name": 2, "os": 2, "version": 1},
        }

        assert aggregator.data == set()

    def test_sync(self):
        client = new_client()
        aggregator = client.context_shape_aggregator

        client.get("some.key", "default", CONTEXT_1)
        client.get("some.key", "default", CONTEXT_2)
        client.get("some.key", "default", CONTEXT_3)

        requests = []

        def new_post(self, *params):
            requests.extend(params)

        funcType = type(client.post)

        client.post = funcType(new_post, client)

        aggregator.sync()

        assert requests == [
            "/api/v1/context-shapes",
            Prefab.ContextShapes(
                shapes=[
                    Prefab.ContextShape(
                        name="device", field_types={"version": 1, "os": 2, "name": 2}
                    ),
                    Prefab.ContextShape(
                        name="subscription",
                        field_types={"plan": 2, "free": 5, "trial": 5},
                    ),
                    Prefab.ContextShape(
                        name="user",
                        field_types={"age": 4, "dob": 2, "email": 2, "name": 2},
                    ),
                ],
            ),
        ]
