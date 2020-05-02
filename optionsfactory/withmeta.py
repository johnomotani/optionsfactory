from collections.abc import Sequence

from ._utils import _checked


class WithMeta:
    """Type for passing metadata with options value or expression into OptionsFactory

    """

    def __init__(self, value, *, doc=None, value_type=None, allowed=None, checks=None):
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
        checks : expression or sequence of expressions, optional
            When a value is set for this option, all the expressions must return True
            when called with that value.
            Cannot be set if 'allowed' is given.
        """
        if isinstance(value, WithMeta):
            if (
                (doc is not None)
                or (value_type is not None)
                or (allowed is not None)
                or (checks is not None)
            ):
                raise ValueError(
                    f"doc={doc}, value_type={value_type}, allowed={allowed}, and "
                    f"checks={checks} should all be None when value is a WithMeta"
                )
            self.value = value.value
            self.doc = value.doc
            self.value_type = value.value_type
            self.allowed = value.allowed
            self.checks = value.checks
            return

        self.value = value
        self.doc = doc

        if isinstance(value_type, Sequence):
            value_type = tuple(value_type)
        self.value_type = value_type

        if (allowed is not None) and (checks is not None):
            raise ValueError("Cannot set both 'allowed' and 'checks'")

        if allowed is not None:
            if (not isinstance(allowed, Sequence)) or isinstance(allowed, str):
                # make allowed values a sequence
                allowed = (allowed,)
            self.allowed = tuple(allowed)
        else:
            self.allowed = None

        if checks is not None:
            if (not isinstance(checks, Sequence)) or isinstance(checks, str):
                # make checks expressions a sequence
                checks = (checks,)
            self.checks = tuple(checks)
            for check in self.checks:
                if not callable(check):
                    raise ValueError(
                        f"{check} is not callable, but was passed as a check"
                    )
        else:
            self.checks = None

    def __eq__(self, other):
        if not isinstance(other, WithMeta):
            return False
        return (
            self.value == other.value
            and self.doc == other.doc
            and self.allowed == other.allowed
            and self.checks == other.checks
        )

    def __str__(self):
        return (
            f"WithMeta({self.value}, doc={self.doc}, value_type={self.value_type}), "
            f"allowed={self.allowed}, checks={self.checks})"
        )

    def evaluate_expression(self, options, *, name=None):
        # Value may be expression or value. Try evaluating as an expression using
        # options first
        default_maybe_expression = self.value
        try:
            default_value = default_maybe_expression(options)
        except TypeError:
            # Try evaluating as name of another option
            if (
                isinstance(default_maybe_expression, str)
                and (
                    not isinstance(self.allowed, Sequence)
                    or default_maybe_expression not in self.allowed
                )
                and (default_maybe_expression in options)
            ):
                default_value = options[default_maybe_expression]
            else:
                default_value = default_maybe_expression

        return _checked(default_value, meta=self, name=name)
