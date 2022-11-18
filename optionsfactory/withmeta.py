from collections.abc import Sequence
from numbers import Number

from ._utils import _checked


class WithMeta:
    """Type for passing metadata with options value or expression into OptionsFactory"""

    def __init__(
        self,
        value,
        *,
        doc=None,
        value_type=None,
        allowed=None,
        check_all=None,
        check_any=None,
    ):
        """
        Parameters
        ----------
        value : expression, value, str, or WithMeta
            - If a callable expression is passed, evaluate expression(options) for the
              default value
            - If a value is passed, used as default value for this option
            - If (i) a str is passed and (ii) it is not in the allowed values for this
              option, and (iii) it is the name of another option, then set the default
              for this option as the value of the other option
            - If a WithMeta object is passed, check no other arguments were set and
              copy all attributes from value
        doc : str, optional
            Docstring for this option
        value_type : type, optional
            Type that this option should have
        allowed : value or sequence of values, optional
            When the option is set, it must have one of these values.
            Cannot be set if 'checks' is given.
        check_all : expression or sequence of expressions, optional
            When a value is set for this option, all the expressions must return True
            when called with that value.
            Cannot be set if 'allowed' is given, but can be combined with check_any.
        check_any : expression or sequence of expressions, optional
            When a value is set for this option, at least one of the expressions must
            return True when called with that value.
            Cannot be set if 'allowed' is given, but can be combined with check_all.
        """
        if isinstance(value, WithMeta):
            if (
                (doc is not None)
                or (value_type is not None)
                or (allowed is not None)
                or (check_all is not None)
                or (check_any is not None)
            ):
                raise ValueError(
                    f"doc={doc}, value_type={value_type}, allowed={allowed}, "
                    f"check_all={check_all}, and check_any={check_any} should all be "
                    f"None when value is a WithMeta"
                )
            self.value = value.value
            self.doc = value.doc
            self.value_type = value.value_type
            self.allowed = value.allowed
            self.check_all = value.check_all
            self.check_any = value.check_any
            return

        if value_type is float and isinstance(value, Number):
            # Allow converting any numerical type to float
            self.value = float(value)
        else:
            self.value = value
        self.doc = doc

        if isinstance(value_type, Sequence):
            value_type = tuple(value_type)
        self.value_type = value_type

        if (allowed is not None) and (check_all is not None or check_any is not None):
            if check_any is None:
                raise ValueError("Cannot set both 'allowed' and 'check_all'")
            elif check_all is None:
                raise ValueError("Cannot set both 'allowed' and 'check_any'")
            else:
                raise ValueError(
                    "Cannot set both 'allowed' and 'check_all' or 'check_any'"
                )

        if allowed is not None:
            if (not isinstance(allowed, Sequence)) or isinstance(allowed, str):
                # make allowed values a sequence
                allowed = (allowed,)
            self.allowed = tuple(allowed)
        else:
            self.allowed = None

        if check_all is not None:
            if (not isinstance(check_all, Sequence)) or isinstance(check_all, str):
                # make check_all expressions a sequence
                check_all = (check_all,)
            self.check_all = tuple(check_all)
            for check in self.check_all:
                if not callable(check):
                    raise ValueError(
                        f"{check} is not callable, but was passed as a check to "
                        f"check_all"
                    )
        else:
            self.check_all = None

        if check_any is not None:
            if (not isinstance(check_any, Sequence)) or isinstance(check_any, str):
                # make check_any expressions a sequence
                check_any = (check_any,)
            self.check_any = tuple(check_any)
            for check in self.check_any:
                if not callable(check):
                    raise ValueError(
                        f"{check} is not callable, but was passed as a check to "
                        f"check_any"
                    )
        else:
            self.check_any = None

    def __eq__(self, other):
        if not isinstance(other, WithMeta):
            return False
        return (
            self.value == other.value
            and self.doc == other.doc
            and self.allowed == other.allowed
            and self.check_all == other.check_all
            and self.check_any == other.check_any
        )

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"WithMeta({self.value}, doc={self.doc}, value_type={self.value_type}), "
            f"allowed={self.allowed}, check_all={self.check_all}, "
            f"check_any={self.check_any})"
        )

    def evaluate_expression(self, options, *, name=None):
        # Value may be expression or value. Try evaluating as an expression using
        # options first
        default_maybe_expression = self.value
        try:
            default_value = default_maybe_expression(options)
        except TypeError:
            # Try evaluating as name of another option, if default_maybe_expression is a
            # str and could not be the value of the option
            if (
                # Can only be a name if self.value is a str
                isinstance(default_maybe_expression, str)
                # Check value_type is set and does not include str, otherwise a string
                # might be the value of the option
                and (self.value_type is not None)
                and (self.value_type is not str)
                and not (
                    isinstance(self.value_type, Sequence) and str in self.value_type
                )
            ):
                try:
                    default_value = options[default_maybe_expression]
                except KeyError:
                    raise KeyError(
                        f"The default {default_maybe_expression}"
                        f"{' for '+str(name) if name is not None else ''} is not in "
                        f"the options"
                    )
            else:
                default_value = default_maybe_expression

        return _checked(default_value, meta=self, name=name)
