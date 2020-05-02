import pytest

from ..optionsfactory import WithMeta
from ..checks import NoneType, is_positive, is_positive_or_None


class TestWithMeta:
    def test_init(self):
        x = WithMeta(1)
        assert x.value == 1

    def test_doc(self):
        x = WithMeta(3.0, doc="option x")
        assert x.doc == "option x"

    def test_value_type(self):
        x = WithMeta(3.0, value_type=float)
        assert x.value_type is float
        assert x.evaluate_expression({}) == 3.0

        x.value = 3
        with pytest.raises(TypeError):
            x.evaluate_expression({})

    def test_value_type_sequence(self):
        x = WithMeta(3.0, value_type=[float, NoneType])
        assert x.evaluate_expression({}) == 3.0

        x.value = None
        assert x.evaluate_expression({}) is None

        x.value = 3
        with pytest.raises(TypeError):
            x.evaluate_expression({})

    def test_allowed(self):
        x = WithMeta("foo", allowed="foo")
        assert x.value == "foo"
        assert x.allowed == ("foo",)
        assert x.evaluate_expression({}) == "foo"
        x.value = "baz"
        with pytest.raises(ValueError):
            x.evaluate_expression({})

    def test_allowed_sequence(self):
        x = WithMeta("foo", allowed=["foo", "bar"])
        assert x.value == "foo"
        assert x.allowed == ("foo", "bar")
        assert x.allowed != ["foo", "bar"]
        assert x.evaluate_expression({}) == "foo"
        x.value = "baz"
        with pytest.raises(ValueError):
            x.evaluate_expression({})

    def test_checks(self):
        x = WithMeta(4.0, checks=is_positive_or_None)
        assert x.value == 4.0
        assert x.evaluate_expression({}) == 4.0
        x.value = -2.0
        with pytest.raises(ValueError):
            x.evaluate_expression({})
        x.value = None
        assert x.evaluate_expression({}) is None

    def test_checks_sequence(self):
        x = WithMeta(5.0, checks=[is_positive, lambda x: x < 6.0])
        assert x.value == 5.0
        assert x.evaluate_expression({}) == 5.0
        x.value = -3.0
        with pytest.raises(ValueError):
            x.evaluate_expression({})
        x.value = 7.0
        with pytest.raises(ValueError):
            x.evaluate_expression({})

    def test_expression_allowed(self):
        x = WithMeta(lambda options: 2.0 * options["foo"], allowed=[4.0, 6.0])
        assert x.evaluate_expression({"foo": 2.0}) == 4.0
        assert x.evaluate_expression({"foo": 3.0}) == 6.0
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": 1.0})

    def test_expression_checks(self):
        x = WithMeta(
            lambda options: 2.0 + options["foo"],
            checks=[is_positive, lambda x: x < 10.0],
        )
        assert x.evaluate_expression({"foo": 2.0}) == 4.0
        assert x.evaluate_expression({"foo": 4.0}) == 6.0
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": -3.0})
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": 9.0})