import pytest

from ..optionsfactory import WithMeta
from ..checks import NoneType, is_positive, is_positive_or_None, is_None


class TestWithMeta:
    def test_init(self):
        x = WithMeta(1)
        assert x.value == 1

    def test_doc(self):
        x = WithMeta(3.0, doc="option x")
        assert x.doc == "option x"

    def test_str_default(self):
        x = WithMeta("b", value_type=float)
        assert x.evaluate_expression({"b": 4.0}) == 4.0
        with pytest.raises(KeyError):
            x.evaluate_expression({"c": 5.0})

    def test_str_default_str_type(self):
        # Should note use "b" as an option name if value_type=str
        x = WithMeta("b", value_type=str)
        assert x.evaluate_expression({"b": "teststr"}) == "b"
        assert x.evaluate_expression({"c": "teststr2"}) == "b"

    def test_str_default_str_in_type(self):
        # Should note use "b" as an option name if str is in value_type
        x = WithMeta("b", value_type=[str, float])
        assert x.evaluate_expression({"b": "teststr"}) == "b"
        assert x.evaluate_expression({"c": "teststr2"}) == "b"

    def test_expression_default(self):
        x = WithMeta(lambda options: options["a"] + options["b"])
        assert x.evaluate_expression({"a": 6.0, "b": 7.0}) == 13.0
        with pytest.raises(KeyError):
            x.evaluate_expression({"c": 6.0, "b": 7.0}) == 13.0

    def test_value_type(self):
        x = WithMeta(3.0, value_type=float)
        assert x.value_type is float
        assert x.evaluate_expression({}) == 3.0

        x.value = 3
        assert x.evaluate_expression({}) == 3.0

    def test_float_conversion(self):
        x = WithMeta(3, value_type=float)
        assert x.value_type is float
        assert x.evaluate_expression({}) == 3.0
        assert isinstance(x.evaluate_expression({}), float)

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

    def test_check_all(self):
        x = WithMeta(4.0, check_all=is_positive_or_None)
        assert x.value == 4.0
        assert x.evaluate_expression({}) == 4.0
        x.value = -2.0
        with pytest.raises(ValueError):
            x.evaluate_expression({})
        x.value = None
        assert x.evaluate_expression({}) is None

    def test_check_all_sequence(self):
        x = WithMeta(5.0, check_all=[is_positive, lambda x: x < 6.0])
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

    def test_expression_check_all(self):
        x = WithMeta(
            lambda options: 2.0 + options["foo"],
            check_all=[is_positive, lambda x: x < 10.0],
        )
        assert x.evaluate_expression({"foo": 2.0}) == 4.0
        assert x.evaluate_expression({"foo": 4.0}) == 6.0
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": -3.0})
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": 9.0})

    def test_check_any(self):
        x = WithMeta(4.0, check_any=is_positive_or_None)
        assert x.value == 4.0
        assert x.evaluate_expression({}) == 4.0
        x.value = -2.0
        with pytest.raises(ValueError):
            x.evaluate_expression({})
        x.value = None
        assert x.evaluate_expression({}) is None

    def test_check_any_sequence(self):
        x = WithMeta(5.0, check_any=[is_positive, lambda x: x < -6.0])
        assert x.value == 5.0
        assert x.evaluate_expression({}) == 5.0
        x.value = -7.0
        assert x.evaluate_expression({}) == -7.0
        x.value = -3.0
        with pytest.raises(ValueError):
            x.evaluate_expression({})

    def test_expression_check_any(self):
        x = WithMeta(
            lambda options: 2.0 + options["foo"],
            check_any=[is_positive, lambda x: x < -10.0],
        )
        assert x.evaluate_expression({"foo": 2.0}) == 4.0
        assert x.evaluate_expression({"foo": -14.0}) == -12.0
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": -3.0})
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": -11.0})

    def test_combined_check_all_any(self):
        x = WithMeta(
            5.0,
            check_all=is_positive,
            check_any=[lambda x: x < 10.0, is_None],
        )
        assert x.evaluate_expression({}) == 5.0
        x.value = -2.0
        with pytest.raises(ValueError):
            x.evaluate_expression({})
        x.value = 10.5
        with pytest.raises(ValueError):
            x.evaluate_expression({})
        x.value = None
        with pytest.raises(ValueError):
            x.evaluate_expression({})

    def test_combined_check_all_any_expression(self):
        x = WithMeta(
            lambda options: -1.0 * options["foo"],
            check_all=is_positive,
            check_any=[lambda x: x < 10.0, is_None],
        )
        assert x.evaluate_expression({"foo": -5.0}) == 5.0
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": 2.0})
        with pytest.raises(ValueError):
            x.evaluate_expression({"foo": -10.5})
        x.value = None
        with pytest.raises(ValueError):
            x.evaluate_expression({})
