from collections.abc import Sequence
from numbers import Number


def _checked(value, *, meta=None, name=None):
    if (meta is not None) and meta.value_type is float and isinstance(value, Number):
        # Allow converting any numerical type to float
        value = float(value)
    if (
        (meta is not None)
        and (meta.value_type is not None)
        and (not isinstance(value, meta.value_type))
    ):
        raise TypeError(
            f"{value} is not of type {_stringify_sequence_of_types(meta.value_type)}"
            f"{'' if name is None else ' for key=' + str(name)}"
        )

    if meta.allowed is not None:
        if value not in meta.allowed:
            raise ValueError(
                f"{value} is not in the allowed values {meta.allowed}"
                f"{'' if name is None else ' for key=' + str(name)}"
            )

    if meta.check_all is not None:
        for check in meta.check_all:
            if not check(value):
                raise ValueError(
                    f"The value {value}"
                    f"{'' if name is None else ' of key=' + str(name)} is not "
                    f"compatible with check_all"
                )

    if meta.check_any is not None:
        success = False
        for check in meta.check_any:
            if check(value):
                success = True
        if not success:
            raise ValueError(
                f"The value {value}"
                f"{'' if name is None else ' of key=' + str(name)} is not "
                f"compatible with check_any"
            )

    return value


def _options_table_string(options):
    """Return a string containing a table of options set"""
    formatstring = "{:<50}|  {:<27}\n"
    defaultformat = "{:<15} (default) "

    # Header
    result = (
        "\nOptions\n=======\n" + formatstring.format("Name", "Value") + "=" * 80 + "\n"
    )

    def _options_table_subsection(options, subsection_name):
        result = ""

        # subsection header
        if subsection_name is not None:
            result += (
                "-" * 80 + "\n" + "{:<80}\n".format(subsection_name) + "-" * 80 + "\n"
            )

        # Row for each value that is not a subsection
        for name, value in sorted(options.items()):
            if name in options.get_subsections():
                continue
            valuestring = str(value)
            if options.is_default(name):
                valuestring = defaultformat.format(valuestring)
            result += formatstring.format(name, valuestring)

        for name in options.get_subsections():
            result += _options_table_subsection(
                options[name],
                f"{str(subsection_name) + ':' if subsection_name is not None else ''}"
                f"{name}",
            )

        return result

    result += _options_table_subsection(options, None)

    return result


def _stringify_sequence_of_types(types):
    if isinstance(types, Sequence):
        return tuple(_stringify_sequence_of_types(t) for t in types)
    else:
        return types.__name__
