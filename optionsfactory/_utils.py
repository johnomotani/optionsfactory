def _checked(value, *, meta=None, name=None):
    if (
        (meta is not None)
        and (meta.value_type is not None)
        and (not isinstance(value, meta.value_type))
    ):
        raise TypeError(
            f"{value} is not of type {meta.value_type}"
            f"{'' if name is None else ' for key=' + str(name)}"
        )

    if meta.allowed is not None:
        if value not in meta.allowed:
            raise ValueError(
                f"{value} is not in the allowed values {meta.allowed}"
                f"{'' if name is None else ' for key=' + str(name)}"
            )

    if meta.checks is not None:
        for check in meta.checks:
            if not check(value):
                raise ValueError(
                    f"The value {value}"
                    f"{'' if name is None else ' of key=' + str(name)} is not "
                    f"compatible with the checks"
                )

    return value


def _options_table_string(options):
    """Return a string containing a table of options set"""
    formatstring = "{:<50}|  {:<30}\n"

    # Header
    result = (
        "\nOptions\n=======\n" + formatstring.format("Name", "Value") + "-" * 80 + "\n"
    )

    # Row for each value
    for name, value in sorted(options.items()):
        valuestring = str(value)
        if options.is_default(name):
            valuestring += "\t(default)"
        result += formatstring.format(name, valuestring)
    return result
