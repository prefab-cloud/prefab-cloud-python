from prefab_cloud_python.context import (
    Context,
    NamedContext,
    InvalidContextFormatException,
)
import pytest
import re


EXAMPLE_PROPERTIES = {
    "user": {"key": "some-user-key", "name": "Ted"},
    "team": {"key": "abc", "plan": "pro"},
}


@pytest.fixture
def setup():
    Context.set_current(None)
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
        assert re.compile(
            "Prefab contexts should be a dict with a key of the context name and a value of a dict of the context"
        ).match(captured.out)

    def test_init_with_invalid_argument(self, setup):
        with pytest.raises(InvalidContextFormatException) as exception:
            Context([])
            assert "Expected a NamedConstant or dict" in str(exception)

    def test_current(self, setup):
        context = Context.get_current()
        assert isinstance(context, Context)
        assert not context.contexts

    def test_current_set(self, setup):
        context = Context(EXAMPLE_PROPERTIES)
        Context.set_current(context)
        assert isinstance(Context.get_current(), Context)
        assert Context.get_current().contexts["user"].get("key") == "some-user-key"

    def test_merge_with_current(self, setup):
        context = Context(EXAMPLE_PROPERTIES)
        Context.set_current(context)
        assert Context.get_current().contexts["user"].get("key") == "some-user-key"

        new_context = Context.merge_with_current(
            {
                "user": {"key": "brand-new", "other": "different"},
                "address": {"city": "New York"},
            }
        )
        assert new_context.to_dict() == {
            "user": {"key": "brand-new", "other": "different"},
            "team": {"key": "abc", "plan": "pro"},
            "address": {"city": "New York"},
        }

        assert Context.get_current().contexts["user"].to_dict() == {
            "key": "some-user-key",
            "name": "Ted",
        }

    def test_with_context(self, setup):
        assert not Context.get_current().contexts
        context = Context(EXAMPLE_PROPERTIES)
        with Context.scope(context):
            assert Context.get_current().contexts["user"].get("key") == "some-user-key"

        assert not Context.get_current().contexts

    def test_nested_with_context(self, setup):
        assert not Context.get_current().contexts
        context = Context(EXAMPLE_PROPERTIES)
        with Context.scope(context):
            with Context.scope({"user": {"key": "michael"}}):
                assert Context.get_current().contexts["user"].get("key") == "michael"

        assert not Context.get_current().contexts

    def test_setting(self, setup):
        context = Context()
        context.set("user", {"key": "value"})
        context["other"] = {"key": "different", "something": "other"}
        assert context["other.key"] == "different"
        assert context["user.key"] == "value"

    def test_getting(self, setup):
        context = Context(EXAMPLE_PROPERTIES)
        assert context.get("user.key") == "some-user-key"
        assert context["user.key"] == "some-user-key"
        assert context.get("team.plan") == "pro"
        assert context["team.plan"] == "pro"

    def test_merge(self, setup):
        context = Context(EXAMPLE_PROPERTIES)
        context.merge("other", {"key": "different"})
        assert context["user.key"] == "some-user-key"
        assert context["other.key"] == "different"

    def test_clear(self, setup):
        context = Context(EXAMPLE_PROPERTIES)
        context.clear()

        assert not context.to_dict()
