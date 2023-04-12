from prefab_cloud_python import Options, Client
import prefab_pb2 as Prefab


class TestConfigLoader:
    def test_calc_config(self):
        client = self.client()
        loader = client.config_client().config_loader

        self.assert_correct_config(loader, "sample_int", "int", 123)
        self.assert_correct_config(loader, "sample", "string", "test sample value")
        self.assert_correct_config(loader, "sample_bool", "bool", True)
        self.assert_correct_config(loader, "sample_double", "double", 12.12)

        self.assert_correct_config(
            loader, "nested.values.string", "string", "nested value"
        )
        self.assert_correct_config(loader, "nested.values", "string", "top level")

        self.assert_correct_config(
            loader, "log-level.app", "log_level", Prefab.LogLevel.Value("ERROR")
        )
        self.assert_correct_config(
            loader,
            "log-level.app.controller.hello",
            "log_level",
            Prefab.LogLevel.Value("WARN"),
        )
        self.assert_correct_config(
            loader,
            "log-level.app.controller.hello.index",
            "log_level",
            Prefab.LogLevel.Value("INFO"),
        )
        self.assert_correct_config(
            loader,
            "log-level.invalid",
            "log_level",
            Prefab.LogLevel.Value("NOT_SET_LOG_LEVEL"),
        )

    def test_calc_config_without_unit_tests(self):
        options = Options(
            prefab_config_classpath_dir="tests", prefab_datasources="LOCAL_ONLY"
        )
        client = Client(options)
        loader = client.config_client().config_loader

        self.assert_correct_config(loader, "sample", "string", "default sample value")
        self.assert_correct_config(loader, "sample_bool", "bool", True)

    def test_highwater(self):
        client = self.client()
        loader = client.config_client().config_loader

        assert loader.highwater_mark == 0
        loader.set(
            Prefab.Config(
                id=1,
                key="sample_int",
                rows=[
                    Prefab.ConfigRow(
                        values=[
                            Prefab.ConditionalValue(value=Prefab.ConfigValue(int=456))
                        ]
                    )
                ],
            ),
            "test",
        )
        assert loader.highwater_mark == 1
        loader.set(
            Prefab.Config(
                id=5,
                key="sample_int",
                rows=[
                    Prefab.ConfigRow(
                        values=[
                            Prefab.ConditionalValue(value=Prefab.ConfigValue(int=456))
                        ]
                    )
                ],
            ),
            "test",
        )
        assert loader.highwater_mark == 5
        loader.set(
            Prefab.Config(
                id=2,
                key="sample_int",
                rows=[
                    Prefab.ConfigRow(
                        values=[
                            Prefab.ConditionalValue(value=Prefab.ConfigValue(int=456))
                        ]
                    )
                ],
            ),
            "test",
        )
        assert loader.highwater_mark == 5

    def test_api_precedence(self):
        client = self.client()
        loader = client.config_client().config_loader

        self.assert_correct_config(loader, "sample_int", "int", 123)

        loader.set(
            Prefab.Config(
                key="sample_int",
                rows=[
                    Prefab.ConfigRow(
                        values=[
                            Prefab.ConditionalValue(value=Prefab.ConfigValue(int=456))
                        ]
                    )
                ],
            ),
            "test",
        )

        self.assert_correct_config(loader, "sample_int", "int", 456)

    def test_api_deltas(self):
        client = self.client()
        loader = client.config_client().config_loader

        val = Prefab.ConfigValue(int=456)
        config = Prefab.Config(
            id=2,
            key="sample_int",
            rows=[Prefab.ConfigRow(values=[Prefab.ConditionalValue(value=val)])],
        )
        loader.set(config, "test")

        configs = Prefab.Configs()
        configs.configs.append(config)

        assert loader.get_api_deltas() == configs

    def test_loading_tombstone_removes_entries(self):
        client = self.client()
        loader = client.config_client().config_loader

        val = Prefab.ConfigValue(int=456)
        config = Prefab.Config(
            id=2,
            key="sample_int",
            rows=[Prefab.ConfigRow(values=[Prefab.ConditionalValue(value=val)])],
        )
        loader.set(config, "test")
        self.assert_correct_config(loader, "sample_int", "int", 456)

        config = Prefab.Config(id=3, key="sample_int", rows=[])
        loader.set(config, "test")

        assert loader.get_api_deltas() == Prefab.Configs()

    @staticmethod
    def assert_correct_config(loader, key, type, value):
        value_from_config = loader.calc_config()[key]["config"].rows[0].values[0].value
        assert value_from_config.WhichOneof("type") == type
        assert getattr(value_from_config, type) == value

    @staticmethod
    def client():
        options = Options(
            prefab_config_classpath_dir="tests",
            prefab_envs="unit_tests",
            prefab_datasources="LOCAL_ONLY",
        )
        return Client(options)
