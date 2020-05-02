import pytest

from ..checks import (
    is_positive,
    is_positive_or_None,
    is_non_negative,
    is_non_negative_or_None,
)


class TestValueCheckUtilities:
    def test_is_positive(self):
        assert is_positive(1)
        assert not is_positive(-1)
        assert not is_positive(0.0)
        with pytest.raises(TypeError):
            is_positive(None)

    def test_is_positive_or_None(self):
        assert is_positive_or_None(1)
        assert not is_positive_or_None(-1)
        assert not is_positive_or_None(0.0)
        assert is_positive_or_None(None)

    def test_is_non_negative(self):
        assert is_non_negative(1)
        assert not is_non_negative(-1)
        assert is_non_negative(0.0)
        with pytest.raises(TypeError):
            is_non_negative(None)

    def test_is_non_negative_or_None(self):
        assert is_non_negative_or_None(1)
        assert not is_non_negative_or_None(-1)
        assert is_non_negative_or_None(0.0)
        assert is_non_negative_or_None(None)
