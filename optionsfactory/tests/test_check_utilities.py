from ..checks import (
    is_positive,
    is_positive_or_None,
    is_non_negative,
    is_non_negative_or_None,
    is_None,
)


class TestValueCheckUtilities:
    def test_is_positive(self):
        assert is_positive(1)
        assert not is_positive(-1)
        assert not is_positive(0.0)
        assert not is_positive(None)

    def test_is_positive_or_None(self):
        assert is_positive_or_None(1)
        assert not is_positive_or_None(-1)
        assert not is_positive_or_None(0.0)
        assert is_positive_or_None(None)

    def test_is_non_negative(self):
        assert is_non_negative(1)
        assert not is_non_negative(-1)
        assert is_non_negative(0.0)
        assert not is_non_negative(None)

    def test_is_non_negative_or_None(self):
        assert is_non_negative_or_None(1)
        assert not is_non_negative_or_None(-1)
        assert is_non_negative_or_None(0.0)
        assert is_non_negative_or_None(None)

    def test_is_None(self):
        assert is_None(None)
        assert not is_None(3.0)
        assert not is_None(-1)
        assert not is_None("foo")
