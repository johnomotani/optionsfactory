from copy import deepcopy

from ._utils import _checked, _options_table_string
from .withmeta import WithMeta


class OptionsFactory:
    """Factory to create Options instances

    """

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
        self.__defaults = {key: WithMeta(value) for key, value in kwargs.items()}

        # Add defaults from *args
        for a in args:
            for key, value in a.items():
                if key in self.__defaults:
                    if value != self.__defaults[key]:
                        raise ValueError(
                            f"{key} has been passed more than once with different "
                            f"values"
                        )
            self.__defaults.update({key: WithMeta(value) for key, value in a.items()})

    @property
    def defaults(self):
        """Get the default values defined for this OptionsFactory

        """
        return deepcopy(self.__defaults)

    def add(self, **kwargs):
        """Create a more specific version of the factory with extra options. For example,
        may be useful for a subclass like

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
            if (not isinstance(value, WithMeta)) and key in new_default_values:
                # just update the default value or expression
                new_default_values[key].value = value
            else:
                new_default_values[key] = value

        return OptionsFactory(new_default_values)

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
        return self._create_immutable(values)

    def _create_mutable(self, values=None):
        if values is None:
            values = {}

        # do not modify passed-in values
        values = deepcopy(dict(values))

        # ignore values for keys not in the list of keys defined in the factory
        for key in list(values):
            if key not in self.__defaults:
                del values[key]

        # Return new MutableOptions instance
        return OptionsFactory.MutableOptions(values, self.__defaults)

    def _create_immutable(self, values=None):
        # Create MutableOptions instance: use to check the values and evaluate defaults
        mutable_options = self._create_mutable(values)

        # make a list of the explicitly-set (non-default) values
        is_default = {key: mutable_options.is_default(key) for key in mutable_options}

        # Return new Options instance
        return OptionsFactory.Options(
            dict(mutable_options),
            {key: self.__defaults[key].doc for key in self.__defaults},
            is_default,
        )

    class MutableOptions:
        """Provide access to a pre-defined set of options, with default values that may
        depend on the values of other options

        """

        def __init__(self, data, defaults):
            self.__defaults = defaults
            self.__data = {
                key: _checked(value, meta=self.__defaults[key], name=key)
                for key, value in data.items()
            }
            self.__cache = {}

        @property
        def doc(self):
            return {key: deepcopy(value.doc) for key, value in self.__defaults.items()}

        def as_table(self):
            """Returns a string with a formatted table of the settings
            """
            return _options_table_string(self)

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
            # Default values may change, so reset the cache
            self.__cache = {}
            self.__data[key] = _checked(value, meta=self.__defaults[key], name=key)

        def __delitem__(self, key):
            # Default values may change, so reset the cache
            self.__cache = {}
            del self.__data[key]

        def __getattr__(self, key):
            if key in self.__defaults:
                return self.__getitem__(key)
            raise AttributeError(f"This MutableOptions has no attribute {key}.")

        def __setattr__(self, key, value):
            if hasattr(super(), "_MutableOptions__defaults") and key in self.__defaults:
                self.__setitem__(key, value)
            super().__setattr__(key, value)

        def __delattr__(self, key):
            if key in self.__data:
                return self.__delitem__(key)
            elif key in self.__defaults:
                # key is one of the options, but not set so don't need to do anything
                return
            super().__delattr__(key)

        def is_default(self, key):
            if key not in self.__defaults:
                raise KeyError(f"{key} is not in this Options")
            return key not in self.__data

        def __contains__(self, key):
            return key in self.__defaults

        def __len__(self):
            return len(self.__defaults)

        def __iter__(self):
            return iter({key: value for key, value in self.items()})

        def keys(self):
            return [key for key in self.__defaults]

        def values(self):
            return [self[key] for key in self.__defaults]

        def items(self):
            return zip(self.keys(), self.values())

        def __str__(self):
            string = "{"
            for key in self.__defaults:
                string += f"{key}: {self[key]}"
                if key not in self.__data:
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

        def __init__(self, data, doc, is_default):
            self.__data = data
            self.__doc = doc
            self.__is_default = is_default

            # Set self.__frozen to True to prevent attributes being changed
            self.__frozen = True

        @property
        def doc(self):
            return deepcopy(self.__doc)

        def as_table(self):
            """Returns a string with a formatted table of the settings
            """
            return _options_table_string(self)

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
                return super.__getattr__(key)
            if key in self.__data:
                return self.__getitem__(key)
            try:
                return super.__getattr__(key)
            except AttributeError:
                raise AttributeError(f"This Options has no attribute {key}.")

        def __setattr__(self, key, value):
            if self.__frozen:
                raise TypeError("Options does not allow assigning to attributes")
            super().__setattr__(key, value)

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
            return iter(deepcopy(self.__data))

        def keys(self):
            return [key for key in self]

        def values(self):
            return [deepcopy(v) for v in self.__data.values()]

        def items(self):
            return zip(self.keys(), self.values())

        def __str__(self):
            return str(self.__data)


class MutableOptionsFactory(OptionsFactory):
    """Factory to create MutableOptions or Options instances

    """

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
        return self._create_mutable(values)

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
        return self._create_immutable(values)
