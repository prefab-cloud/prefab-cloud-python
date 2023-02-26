from prefab_cloud_python.criteria_evaluator import CriteriaEvaluator
import prefab_pb2 as Prefab

project_env_id = 1
test_env_id = 2
key = "key"
default_value = "default_value"
desired_value = "desired_value"
wrong_env_value = "wrong_env_value"

default_row = Prefab.ConfigRow(
    values=[
        Prefab.ConditionalValue(
            value=Prefab.ConfigValue(string=default_value)
        )
    ]
)

class TestCriteriaEvaluator:
    def test_always_true(self):
        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(operator="ALWAYS_TRUE")
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=None, base_client=None)
        assert evaluator.evaluate({}).string == desired_value

    def test_lookup_key_in(self):
        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="LOOKUP_KEY_IN",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["ok", "fine"])
                                    ),
                                    property_name="LOOKUP"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=None, base_client=None)

        assert evaluator.evaluate({}).string == default_value
        assert evaluator.evaluate({"LOOKUP": "wrong"}).string == default_value
        assert evaluator.evaluate({"LOOKUP": "ok"}).string == desired_value


    def test_lookup_key_not_in(self):
        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="LOOKUP_KEY_NOT_IN",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["wrong", "bad"])
                                    ),
                                    property_name="LOOKUP"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=None, base_client=None)

        assert evaluator.evaluate({}).string == desired_value
        assert evaluator.evaluate({"LOOKUP": "wrong"}).string == default_value
        assert evaluator.evaluate({"LOOKUP": "ok"}).string == desired_value

    def test_prop_is_one_of(self):
        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["hotmail.com", "gmail.com"])
                                    ),
                                    property_name="email_suffix"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=None, base_client=None)

        assert evaluator.evaluate({}).string == default_value
        assert evaluator.evaluate({"email_suffix": "prefab.cloud"}).string == default_value
        assert evaluator.evaluate({"email_suffix": "hotmail.com"}).string == desired_value

    def test_prop_is_not_one_of(self):
        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_NOT_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["hotmail.com", "gmail.com"])
                                    ),
                                    property_name="email_suffix"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=None, base_client=None)

        assert evaluator.evaluate({}).string == desired_value
        assert evaluator.evaluate({"email_suffix": "prefab.cloud"}).string == desired_value
        assert evaluator.evaluate({"email_suffix": "hotmail.com"}).string == default_value

    def test_prop_ends_with_one_of(self):
        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_ENDS_WITH_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["hotmail.com", "gmail.com"])
                                    ),
                                    property_name="email"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=None, base_client=None)

        assert evaluator.evaluate({}).string == default_value
        assert evaluator.evaluate({"email": "example@prefab.cloud"}).string == default_value
        assert evaluator.evaluate({"email": "example@hotmail.com"}).string == desired_value

    def test_prop_does_not_end_with_one_of(self):
        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_DOES_NOT_END_WITH_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["hotmail.com", "gmail.com"])
                                    ),
                                    property_name="email"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=None, base_client=None)

        assert evaluator.evaluate({}).string == desired_value
        assert evaluator.evaluate({"email": "example@prefab.cloud"}).string == desired_value
        assert evaluator.evaluate({"email": "example@hotmail.com"}).string == default_value

    def test_in_seg(self):
        segment_key = "segment_key"

        segment_config = Prefab.Config(
            config_type="SEGMENT",
            key=segment_key,
            rows=[
                Prefab.ConfigRow(
                    values=[
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=True),
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_ENDS_WITH_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["hotmail.com", "gmail.com"])
                                    ),
                                    property_name="email"
                                )
                            ]
                        ),
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=False)
                        )
                    ]
                )
            ]
        )

        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                # wrong env,
                Prefab.ConfigRow(
                    project_env_id=test_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="IN_SEG",
                                    value_to_match=Prefab.ConfigValue(string=segment_key)
                                )
                            ],
                            value=Prefab.ConfigValue(string=wrong_env_value)
                        )
                    ]
                ),
                # correct env
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="IN_SEG",
                                    value_to_match=Prefab.ConfigValue(string=segment_key)
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=self.mock_resolver({segment_key: segment_config}), base_client=None)

        assert evaluator.evaluate({}).string == "default_value"
        assert evaluator.evaluate({"email": "example@prefab.cloud"}).string == "default_value"
        assert evaluator.evaluate({"email": "example@hotmail.com"}).string == "desired_value"

    def test_not_in_seg(self):
        segment_key = "segment_key"

        segment_config = Prefab.Config(
            config_type="SEGMENT",
            key=segment_key,
            rows=[
                Prefab.ConfigRow(
                    values=[
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=True),
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_ENDS_WITH_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["hotmail.com", "gmail.com"])
                                    ),
                                    property_name="email"
                                )
                            ]
                        ),
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=False)
                        )
                    ]
                )
            ]
        )

        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="NOT_IN_SEG",
                                    value_to_match=Prefab.ConfigValue(string=segment_key)
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=self.mock_resolver({segment_key: segment_config}), base_client=None)

        assert evaluator.evaluate({}).string == desired_value
        assert evaluator.evaluate({"email": "example@prefab.cloud"}).string == desired_value
        assert evaluator.evaluate({"email": "example@hotmail.com"}).string == default_value

    def test_multiple_conditions_in_one_value(self):
        segment_key = "segment_key"

        segment_config = Prefab.Config(
            config_type="SEGMENT",
            key=segment_key,
            rows=[
                Prefab.ConfigRow(
                    values=[
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=True),
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_ENDS_WITH_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["prefab.cloud", "gmail.com"])
                                    ),
                                    property_name="email"
                                ),
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(bool=True),
                                    property_name="admin"
                                ),
                            ]
                        ),
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=False)
                        )
                    ]
                )
            ]
        )

        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="IN_SEG",
                                    value_to_match=Prefab.ConfigValue(string=segment_key)
                                ),
                                Prefab.Criterion(
                                    operator="PROP_IS_NOT_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(bool=True),
                                    property_name="deleted"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=self.mock_resolver({segment_key: segment_config}), base_client=None)

        assert evaluator.evaluate({}).string == default_value
        assert evaluator.evaluate({"email": "example@prefab.cloud"}).string == default_value
        assert evaluator.evaluate({"email": "example@prefab.cloud", "admin": True}).string == desired_value
        assert evaluator.evaluate({"email": "example@prefab.cloud", "admin": True, "deleted": True}).string == default_value
        assert evaluator.evaluate({"email": "example@gmail.com"}).string == default_value
        assert evaluator.evaluate({"email": "example@gmail.com", "admin": True}).string == desired_value
        assert evaluator.evaluate({"email": "example@gmail.com", "admin": True, "deleted": True}).string == default_value

    def test_multiple_conditions_in_multiple_value(self):
        segment_key = "segment_key"

        segment_config = Prefab.Config(
            config_type="SEGMENT",
            key=segment_key,
            rows=[
                Prefab.ConfigRow(
                    values=[
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=True),
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_ENDS_WITH_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(
                                        string_list=Prefab.StringList(values=["prefab.cloud", "gmail.com"])
                                    ),
                                    property_name="email"
                                ),

                            ]
                        ),
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=True),
                            criteria=[
                                Prefab.Criterion(
                                    operator="PROP_IS_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(bool=True),
                                    property_name="admin"
                                ),
                            ]
                        ),
                        Prefab.ConditionalValue(
                            value=Prefab.ConfigValue(bool=False)
                        )
                    ]
                )
            ]
        )

        config = Prefab.Config(
            key=key,
            rows=[
                default_row,
                Prefab.ConfigRow(
                    project_env_id=project_env_id,
                    values=[
                        Prefab.ConditionalValue(
                            criteria=[
                                Prefab.Criterion(
                                    operator="IN_SEG",
                                    value_to_match=Prefab.ConfigValue(string=segment_key)
                                ),
                                Prefab.Criterion(
                                    operator="PROP_IS_NOT_ONE_OF",
                                    value_to_match=Prefab.ConfigValue(bool=True),
                                    property_name="deleted"
                                )
                            ],
                            value=Prefab.ConfigValue(string=desired_value)
                        )
                    ]
                )
            ]
        )

        evaluator = CriteriaEvaluator(config, project_env_id, resolver=self.mock_resolver({segment_key: segment_config}), base_client=None)

        assert evaluator.evaluate({}).string == default_value
        assert evaluator.evaluate({"email": "example@prefab.cloud"}).string == desired_value
        assert evaluator.evaluate({"email": "example@prefab.cloud", "admin": True}).string == desired_value
        assert evaluator.evaluate({"email": "example@prefab.cloud", "admin": True, "deleted": True}).string == default_value
        assert evaluator.evaluate({"email": "example@gmail.com"}).string == desired_value
        assert evaluator.evaluate({"email": "example@gmail.com", "admin": True}).string == desired_value
        assert evaluator.evaluate({"email": "example@gmail.com", "admin": True, "deleted": True}).string == default_value

    @staticmethod
    def mock_resolver(config):
        return MockResolver(config)

class MockResolver:
    def __init__(self, config):
        self.config = config

    def raw(self, key):
        self.config.get(key)

    def get(self, key, _lookup_key, properties={}):
        return CriteriaEvaluator(self.config.get(key), project_env_id=None, resolver=None, base_client=None).evaluate(properties)
