from prefab_cloud_python.context import Context, NamedContext
import pytest
import re


@pytest.fixture
def setup():
    Context.current = None
    yield


class TestContext:
    def test_init_with_empty_context(self, setup):
        context = Context({})
        assert not context.contexts

    def test_init_with_named_context(self, setup):
        named_context = NamedContext("test", {"foo": "bar"})
        context = Context(named_context)
        assert len(context.contexts) == 1
        assert context.contexts["test"] == named_context

    def test_init_with_dict(self, setup):
        context = Context({"test": {"foo": "bar"}})
        assert len(context.contexts) == 1
        assert context.contexts["test"].get("foo") == "bar"

    def test_init_with_multiple_dicts(self, setup):
        context = Context({"test": {"foo": "bar"}, "other": {"foo": "baz"}})
        assert len(context.contexts) == 2
        assert context.contexts["test"].get("foo") == "bar"
        assert context.contexts["other"].get("foo") == "baz"

    def test_init_with_non_hash_values(self, setup, capsys):
        context = Context({"name": "michael"})
        assert len(context.contexts) == 1
        assert context.contexts[""].get("name") == "michael"

        captured = capsys.readouterr()
        assert re.compile("Prefab contexts should be a dict with a key of the context name and a value of a dict of the context").match(captured.out)

