from copy import copy, deepcopy

from ._utils import _checked, _options_table_string
from .withmeta import WithMeta


class OptionsFactory:
    """Factory to create Options instances"""

    def __init__(self, *args, **kwargs):
        """Define the members of Options instances that this factory will create

        Parameters
        ----------
        *args : dicts of {key: [Withmeta, value or expression]}
            These dicts are combined with the kwargs to create the default values for
            this object.  Intended to allow collecting defaults from contained objects.
            For example, if we have a class A, with members from classes B and C which
            each have an OptionsFactory, we could have something like:

                class A:
                    options_factory = OptionsFactory(
                        B.options_factory.defaults,
                        C.options_factory.defaults,
                        extra_option1 = 1,
                        extra_option2 = 2,
                    )

            It is an error for any keys in *args to be repeated or be the same as any in
            **kwargs.
        **kwargs : key=[WithMeta, value or expression]
            Keys are the names of the members of the Options that the factory will
            create.
            If a value is passed, that is used as the default for this key. If an
            expression is passed, it should take one argument, and can access values of
            other Options members from that argument. WithMeta allows values or
            expressions to be passed with extra metadata. For example,

                factory = OptionsFactory(
                    a=1,
                    b=lambda options: options.c + options.a
                    c=lambda options: 3*options["a"]
                    d=WithMeta(
                        4, doc="option d", value_type=int, allowed=[4, 5, 6]
                    )
                    e=WithMeta(
                        lambda options: options.a + options.b + options.c + options.d,
                        doc="option e",
                        value_type=float,
                        checks=lambda x: x > 0.0
                    )
                )
        """
        self.__defaults = {}
        for key, value in kwargs.items():
            if isinstance(value, OptionsFactory):
                self.__defaults[key] = value
            else:
                self.__defaults[key] = WithMeta(value)

        # Add defaults from *args
        for a in args:
            if not isinstance(a, OptionsFactory):
                raise ValueError(
                    f"Positional arguments to OptionsFactory.__init__() must be "
                    f"OptionsFactory instances, was passed a {type(a)}"
                )
            for key, value in a.defaults.items():
                if key in self.__defaults:
                    if value != self.__defaults[key]:
                        raise ValueError(
                            f"{key} has been passed more than once with different "
                            f"values"
                        )
                if isinstance(value, OptionsFactory):
                    self.__defaults[key] = value
                else:
                    self.__defaults[key] = WithMeta(value)

    @property
    def defaults(self):
        """Get the default values defined for this OptionsFactory"""
        return deepcopy(self.__defaults)

    @property
    def doc(self):
        """Get the documentation for the options defined for this OptionsFactory"""
        return {key: value.doc for key, value in self.__defaults.items()}

    def add(self, **kwargs):
        """Create a more specific version of the factory with extra options. For
        example, may be useful for a subclass like

            class Parent:
                options_factory = OptionsFactory(...)

            class Child:
                options_factory = Parent.options_factory.add(
                    an_extra_option="used only by Child"
                )

        Parameters
        ----------
        **kwargs : key=[WithMeta, value or expression]
            The new options to add, these override the ones in the parent factory if key
            already exists, but keep the doc, allowed and checks if the option is just a
            new value/expression (not a new WithMeta)
        """
        new_default_values = deepcopy(self.__defaults)
        for key, value in kwargs.items():
            if key in new_default_values and isinstance(
                new_default_values[key], OptionsFactory
            ):
                if isinstance(value, OptionsFactory):
                    raise ValueError(
                        f"Updating the section {key} in OptionsFactory, but was passed "
                        f"an OptionsFactory. This is forbidden as options from the new "
                        f"OptionsFactory might unexpectedly overwrite metadata in the "
                        f"existing section. Pass a dict instead to update {key}."
                    )
                new_default_values[key] = new_default_values[key].add(**value)
            elif isinstance(value, OptionsFactory):
                if key in new_default_values:
                    raise ValueError(
                        f"Passing an OptionsFactory to OptionsFactory.add() creates a "
                        f"new section, but the option {key} already exists"
                    )
                new_default_values[key] = value
            elif isinstance(value, WithMeta):
                new_default_values[key] = value
            elif key in new_default_values:
                # just update the default value or expression
                new_default_values[key].value = value
            else:
                new_default_values[key] = WithMeta(value)

        # Use type(self) so that OptionsFactory returns an OptionsFactory but
        # MutableOptionsFactory returns a MutableOptionsFactory
        return type(self)(**new_default_values)

    def __contains__(self, key):
        return key in self.__defaults

    def create(self, values=None):
        """Create an Options instance

        The members of the created Options are defined by this
        OptionsFactory instance. Any values passed in the values argument are used,
        and the rest are set from defaults, which can be expressions depending on other
        members.

        Parameters
        ----------
        values : dict or Options, optional
            Non-default values to be used
        """
        return self.__create_immutable(values)

    def create_from_yaml(self, file_like):
        """Create an Options instance from an input YAML file

        Parameters
        ----------
        file_like : file handle or similar to read from
            File to read from
        """
        return self.create(self._load_yaml(file_like))

    def _load_yaml(self, file_like):
        import yaml

        return yaml.safe_load(file_like)

    def __create_mutable(self, values=None, parent=None):
        if values is None:
            values = {}

        # do not modify passed-in values
        values = deepcopy(dict(values))

        # ignore values for keys not in the list of keys defined in the factory
        for key in list(values):
            if key not in self.__defaults:
                del values[key]

        # Return new MutableOptions instance
        return OptionsFactory.MutableOptions(
            values, self.__defaults, self.doc, parent=parent
        )

    def __create_immutable(self, values=None):
        # Create MutableOptions instance: use to check the values and evaluate defaults
        mutable_options = self.__create_mutable(values)

        # Return new Options instance
        return OptionsFactory.Options(mutable_options)

    def get_help_table(self, prefix=None, as_Texttable=False):
        """Print a table of the options in this OptionsFactory, with help text and
        default values, either in text using ReStructuredText syntax, or as a
        `texttable.Texttable` object.

        Parameters
        ----------
        prefix : str, default None
            If a value is passed, add `prefix` to the beginning of each line, e.g. to
            add indentation
        as_Texttable : bool, default False
            Return the table
        """
        if prefix is None:
            prefix = ""
        defaults = self.defaults
        evaluated_defaults = {}

        # Need to use self.__create_mutable() here as if any option is required to be
        # set then calling self.create() would cause an error (actually the error we
        # want to catch and handle case-by-case in the try-except below).
        mutable_options = self.__create_mutable()
        for k, v in defaults.items():
            try:
                evaluated = v.evaluate_expression(mutable_options)
            except (ValueError, TypeError):
                # If the default value cannot be evaluated, it is required to be set in
                # `values` when the Options or MutableOptions are created
                evaluated = "*Required*"
            evaluated_defaults[k] = evaluated

        keys = sorted(defaults.keys())
        docs = self.doc
        heading1 = "Option"
        heading2 = "Description"
        heading3 = "Default"
        if as_Texttable:
            try:
                from texttable import Texttable
            except ImportError:
                print(
                    "Please install the `texttable` package to use the `as_TextTable` "
                    "option"
                )
                raise
            tt = Texttable()
            tt.header([heading1, heading2, heading3])
            for k in keys:
                tt.add_row([k, str(docs[k]), str(evaluated_defaults[k])])
            return tt
        else:
            column1_width = max(max(len(k) for k in keys), len(heading1))
            column2_width = max(max(len(str(d)) for d in docs.values()), len(heading2))
            column3_width = max(
                max(len(str(d)) for d in evaluated_defaults.values()), len(heading3)
            )
            separator = (
                prefix
                + "+"
                + "-" * column1_width
                + "+"
                + "-" * column2_width
                + "+"
                + "-" * column3_width
                + "+\n"
            )
            table = separator
            table = (
                table
                + prefix
                + "|"
                + heading1.ljust(column1_width)
                + "|"
                + heading2.ljust(column2_width)
                + "|"
                + heading3.ljust(column3_width)
                + "|\n"
            )
            table = table + (
                prefix
                + "+"
                + "=" * column1_width
                + "+"
                + "=" * column2_width
                + "+"
                + "=" * column3_width
                + "+\n"
            )
            for k in keys:
                table = (
                    table
                    + prefix
                    + "|"
                    + k.ljust(column1_width)
                    + "|"
                    + str(docs[k]).ljust(column2_width)
                    + "|"
                    + str(evaluated_defaults[k]).ljust(column3_width)
                    + "|\n"
                )
                table = table + separator
            return table

    class MutableOptions:
        """Provide access to a pre-defined set of options, with default values that may
        depend on the values of other options

        """

        def __init__(self, data, defaults, doc, parent=None):
            self.__defaults = {
                key: value if not isinstance(value, OptionsFactory) else None
                for key, value in defaults.items()
            }
            self.__cache = {}
            self.__parent = parent

            # don't modify input data
            data = copy(data)

            self.__data = {}
            # Add subsections first
            for subsection in self.get_subsections():
                if subsection in data:
                    subsection_data = data[subsection]
                    del data[subsection]
                else:
                    subsection_data = {}
                self.__data[subsection] = defaults[
                    subsection
                ]._OptionsFactory__create_mutable(subsection_data, parent=self)

            # Add values in this section second - now 'data' contains only values, not
            # subsections
            for key, value in data.items():
                self.__data[key] = _checked(value, meta=self.__defaults[key], name=key)

            self.__doc = doc

        @property
        def doc(self):
            return self.__doc

        @property
        def parent(self):
            return self.__parent

        def as_table(self):
            """Return a string with a formatted table of the settings"""
            return _options_table_string(self)

        def to_dict(self, with_defaults=True):
            """Convert the MutableOptions object to a dict

            Parameters
            ----------
            with_defaults : bool, default True
                Include the default values in the returned dict?
            """
            if with_defaults:
                return {
                    key: value
                    if not isinstance(value, OptionsFactory.MutableOptions)
                    else value.to_dict(with_defaults)
                    for key, value in self.items()
                }
            else:
                return {
                    key: value
                    if not isinstance(value, OptionsFactory.MutableOptions)
                    else value.to_dict(with_defaults)
                    for key, value in self.items()
                    # Use 'is not True' so we include subsections, for which
                    # self.is_default(key) returns a dict
                    if self.is_default(key) is not True
                }

        def to_yaml(self, file_like, with_defaults=False):
            """Save the options to a YAML file

            Save only the non-default options unless with_defaults=True is passed

            Parameters
            ----------
            file_like : file handle or similar
                File to write to
            with_defaults : bool, default False
                Save all the options, including default values
            """
            import yaml

            return yaml.dump(self.to_dict(with_defaults), file_like)

        def get_subsections(self):
            """
            Iterator over the subsections in this MutableOptions
            """
            for key, value in self.__defaults.items():
                # None marks subsections in self.__defaults - all other values are
                # WithMeta objects
                if value is None:
                    yield key

        def __clear_cache(self, is_child=False):
            if self.__parent is None or is_child:
                # Once we have found the root MutableOptions object, follow the tree,
                # clearing the cache of each MutableOptions section or subsection.
                self.__cache = {}
                for subsection in self.get_subsections():
                    self[subsection].__clear_cache(True)
            else:
                # Go up until we find the root MutableOptions object, which has
                # (self.parent is None)
                self.__parent.__clear_cache()

        def __getitem__(self, key):
            if key not in self.__defaults:
                raise KeyError(f"This Options does not contain {key}")

            # If key is already in __cache, then it has a definite value
            if key in self.__cache:
                return self.__cache[key]

            # Check if option was in user-set values
            try:
                value = self.__data[key]
            except KeyError:
                pass
            else:
                self.__cache[key] = value
                return value

            # When setting default values, detect circular definitions
            if not hasattr(self, "_MutableOptions__key_chain"):
                chain_start = True
                self.__key_chain = [key]
            else:
                if key in self.__key_chain:
                    # Found a circular definition

                    # Tidy up object state
                    key_chain = self.__key_chain
                    del self.__key_chain

                    # Tell the user where the circular definition was
                    index = key_chain.index(key)
                    raise ValueError(
                        f"Circular definition of default values. At least one of "
                        f"{key_chain[index:]} must have a definite value"
                    )

                chain_start = False
                self.__key_chain.append(key)

            self.__cache[key] = self.__defaults[key].evaluate_expression(self, name=key)

            if chain_start:
                # Tidy up temporary member variable
                del self.__key_chain

            return self.__cache[key]

        def __setitem__(self, key, value):
            if key not in self.__defaults:
                raise KeyError(
                    f"Tried to set {key}={value} but {key} is not one of the defined "
                    f"options"
                )
            # Default values may change, so reset the cache
            self.__clear_cache()
            self.__data[key] = _checked(value, meta=self.__defaults[key], name=key)

        def __delitem__(self, key):
            if key not in self.__defaults:
                raise KeyError(
                    f"Tried to unset {key} but {key} is not one of the defined options"
                )
            if key in self.__data:
                # Default values may change, so reset the cache
                self.__cache = {}
                del self.__data[key]
            # Otherwise 'key' is a valid option but was not set, so nothing changes

        def __getattr__(self, key):
            if key == "_MutableOptions__defaults":
                return super(OptionsFactory.MutableOptions, self).__getattr__(key)
            if key in self.__defaults:
                return self.__getitem__(key)
            raise AttributeError(f"This MutableOptions has no attribute {key}.")

        def __setattr__(self, key, value):
            if hasattr(self, "_MutableOptions__defaults") and key in self.__defaults:
                return self.__setitem__(key, value)
            super(OptionsFactory.MutableOptions, self).__setattr__(key, value)

        def __delattr__(self, key):
            if key in self.__defaults:
                return self.__delitem__(key)
            super(OptionsFactory.MutableOptions, self).__delattr__(key)

        def is_default(self, key):
            if key not in self.__defaults:
                raise KeyError(f"{key} is not in this Options")
            value = self[key]
            if isinstance(value, OptionsFactory.MutableOptions):
                return {k: value.is_default(k) for k in value}
            return key not in self.__data

        def __contains__(self, key):
            return key in self.__defaults

        def __len__(self):
            return len(self.__defaults)

        def __iter__(self):
            return iter(self.keys())

        def keys(self):
            return self.__defaults.keys()

        def values(self):
            for key in self:
                yield self[key]

        def items(self):
            return zip(self.keys(), self.values())

        def __str__(self):
            string = "{"
            for key in self.__defaults:
                value = self[key]
                string += f"{key}: {value}"

                # Using 'is True' here means we only append ' (default)' to options, not
                # sections: if 'key' is a section then self.is_default(key) will return
                # a dict
                if self.is_default(key) is True:
                    string += " (default)"
                string += ", "
            if len(string) > 1:
                # remove trailing ", "
                string = string[:-2]
            string += "}"
            return string

    class Options:
        """Provide access to a pre-defined set of options, with values fixed when the
        instance is created

        """

        __frozen = False

        def __init__(self, mutable_options):
            self.__data = {}
            for key, value in mutable_options.items():
                if isinstance(value, OptionsFactory.MutableOptions):
                    self.__data[key] = OptionsFactory.Options(mutable_options[key])
                else:
                    self.__data[key] = deepcopy(value)

            self.__doc = deepcopy(mutable_options.doc)

            # make a dict of the explicitly-set (non-default) values
            self.__is_default = {
                key: mutable_options.is_default(key) for key in mutable_options
            }

            # Set self.__frozen to True to prevent attributes being changed
            self.__frozen = True

        @property
        def doc(self):
            return deepcopy(self.__doc)

        def as_table(self):
            """Return a string with a formatted table of the settings"""
            return _options_table_string(self)

        def to_dict(self, with_defaults=True):
            """Convert the MutableOptions object to a dict

            Parameters
            ----------
            with_defaults : bool, default True
                Include the default values in the returned dict?
            """
            if with_defaults:
                return {
                    key: value
                    if not isinstance(value, OptionsFactory.Options)
                    else value.to_dict(with_defaults)
                    for key, value in self.items()
                }
            else:
                return {
                    key: value
                    if not isinstance(value, OptionsFactory.Options)
                    else value.to_dict(with_defaults)
                    for key, value in self.items()
                    # Use 'is not True' so we include subsections, for which
                    # self.is_default(key) returns a dict
                    if self.is_default(key) is not True
                }

        def to_yaml(self, file_like, with_defaults=False):
            """Save the options to a YAML file

            Save only the non-default options unless with_defaults=True is passed

            Parameters
            ----------
            file_like : file handle or similar
                File to write to
            with_defaults : bool, default False
                Save all the options, including default values
            """
            import yaml

            return yaml.dump(self.to_dict(with_defaults), file_like)

        def get_subsections(self):
            """
            Iterator over the subsections in this Options
            """
            for key, value in self.__data.items():
                if isinstance(value, OptionsFactory.Options):
                    yield key

        def __getitem__(self, key):
            try:
                return deepcopy(self.__data.__getitem__(key))
            except KeyError:
                raise KeyError(f"This Options does not contain {key}")

        def __setitem__(self, key, value):
            raise TypeError("Options does not allow assigning to keys")

        def __getattr__(self, key):
            if key == "_Options__data":
                # need to treat __data specially, as we use it for the next test
                return super(OptionsFactory.Options, self).__getattr__(key)
            if key in self.__data:
                return self.__getitem__(key)
            try:
                return super(OptionsFactory.Options, self).__getattr__(key)
            except AttributeError:
                raise AttributeError(f"This Options has no attribute {key}.")

        def __setattr__(self, key, value):
            if self.__frozen:
                raise TypeError("Options does not allow assigning to attributes")
            super(OptionsFactory.Options, self).__setattr__(key, value)

        def __getstate__(self):
            # Need to define this so that pickling with dill works
            return vars(self)

        def __setstate__(self, state):
            # Need to define this so that pickling with dill works
            vars(self).update(state)

        def is_default(self, key):
            try:
                return self.__is_default[key]
            except KeyError:
                raise KeyError(f"{key} is not in this Options")

        def __contains__(self, key):
            return key in self.__data

        def __len__(self):
            return len(self.__data)

        def __iter__(self):
            return iter(self.keys())

        def keys(self):
            return self.__data.keys()

        def values(self):
            for v in self.__data.values():
                yield deepcopy(v)

        def items(self):
            return zip(self.keys(), self.values())

        def __str__(self):
            string = "{"
            for key in self.__data:
                string += f"{key}: {self[key]}"

                # Using 'is True' here means we only append ' (default)' to options, not
                # sections: if 'key' is a section then self.is_default(key) will return
                # a dict
                if self.is_default(key) is True:
                    string += " (default)"
                string += ", "
            if len(string) > 1:
                # remove trailing ", "
                string = string[:-2]
            string += "}"
            return string


class MutableOptionsFactory(OptionsFactory):
    """Factory to create MutableOptions or Options instances"""

    def create(self, values=None):
        """Create a MutableOptions instance

        The members of the created MutableOptions are defined by this
        MutableOptionsFactory instance. Any values passed in the values argument are
        used, and the rest are set from defaults, which can be expressions depending on
        other members.

        Parameters
        ----------
        values : dict or Options, optional
            Non-default values to be used
        """
        return self._OptionsFactory__create_mutable(values)

    def create_immutable(self, values=None):
        """Create an Options instance (which is immutable)

        The members of the created Options are defined by this
        MutableOptionsFactory instance. Any values passed in the values argument are
        used, and the rest are set from defaults, which can be expressions depending on
        other members.

        Parameters
        ----------
        values : dict or Options, optional
            Non-default values to be used
        """
        return self._OptionsFactory__create_immutable(values)

    def create_from_yaml(self, file_like):
        """Create a MutableOptions instance from an input YAML file

        Parameters
        ----------
        file_like : file handle or similar to read from
            File to read from
        """
        return self.create(self._load_yaml(file_like))

    def create_immutable_from_yaml(self, file_like):
        """Create an Options instance (which is immutable) from an input YAML file

        Parameters
        ----------
        file_like : file handle or similar to read from
            File to read from
        """
        return self.create_immutable(self._load_yaml(file_like))
