`OptionsFactory`
================

https://github.com/johnomotani/optionsfactory

`OptionsFactory` allows you to define a set of options, which can have (if you like):
default values (which may be expressions depending on other options); documentation for
each option; an allowed type or list of types; a check that the value option is on an
allowed list; checks that the value of an option satisfies some tests.

Once the options are defined in an `OptionsFactory`, you create a particular instance of
the options by passing some user settings (a dict or YAML file). The `OptionsFactory`
uses the values passed, sets the remaining options from the default values or
expressions and returns an `Options` object. Options are immutable so that you do not
have to worry about the options being accidentally changed during execution - however,
see [`MutableOptionsFactory`](#mutableoptionsfactory) if you want to be able to update the
options dynamically.

For example, some simple options might be implemented like this:
```python
from optionsfactory import OptionsFactory


class A:

    # The keyword arguments define the options and give the default values
    options_factory = OptionsFactory(a=1, b=2)

    def __init__(self, user_options = None):
        self.options = self.options_factory.create(user_options)

        # options can be accessed like a dict
        myvalue = 2 * options["a"]

        #... or as attributes
        mynewvalue = 3 + options.a
```

It might also be useful for some classes to allow the options to be set from keyword
arguments, for example
```python
from optionsfactory import OptionsFactory


class B:

    # The keyword arguments define the options and give the default values
    options_factory = OptionsFactory(a=1, b=2)

    def __init__(self, **kwargs):
        self.options = self.options_factory.create(kwargs)
```
The `create()` method will not alter the argument passed to it.

The options will then combine explicitly set values and defaults:
```python
>>> b1 = B() # uses default values
>>> b1.options.a
1
>>> b1.options.b
2
>>> b2 = B(b=4) # override one of the defaults
>>> b2.options.a
1
>>> b2.options.b
4
```

More flexibility is available by using expressions to set the default values.
```python
from optionsfactory import OptionsFactory


class C:

    # The keyword arguments define the options and give the default values
    options_factory = OptionsFactory(a=lambda options: options.b + 5, b=2)

    def __init__(self, **kwargs):
        self.options = self.options_factory.create(kwargs)
```
could be used like:
```python
>>> c1 = C() # only default values
>>> c1.options.a
7
>>> c1.options.b
2
>>> c2 = C(a=1, b=3) # override both options, expression not used
>>> c2.options.a
1
>>> c2.options.b
>>> 3
>>> c3 = C(b=4) # User-set value of b evaluated in default expression for a
>>> c3.options.a
9
>>> c3.options.b
4
```
Circular dependencies in expressions will be detected and raise a ValueError.


`WithMeta`
----------

`WithMeta` objects are used to store the defaults within `OptionsFactory`, and can be
used to define options with extra information, e.g.
```python
from optionsfactory import OptionsFactory, WithMeta
from optionsfactory.checks import is_positive, is_None


class D:
    options_factory = OptionsFactory(
        a=WithMeta(1, doc="option a"),
        b=WithMeta(2, value_type=int),
        c=WithMeta(3, allowed=[1, 2, 3]),
        d=WithMeta(4, check_all=is_positive),
        e=WithMeta(5, check_any=lambda x: x < 6),
        f=WithMeta(6, doc="option f", value_type=[int, float], allowed=[6, 7, 8, 9.5]),
        g=WithMeta(
            7,
            doc="option g",
            value_type=[int, None],
            check_all=[is_positive, lambda x: x < 10],
            check_any=[lambda x: x < 2, lambda x: x > 6],
        ),
    )

    def __init__(self, **kwargs):
        self.options = self.options_factory.create(kwargs)
```
The first argument to `WithMeta` gives the default value for the option, and the
remaining keyword arguments are all optional. Using `WithMeta` the values behave just as
the simple default values described above:
```python
>>> d = D(b=12)
>>> d.options.a
1
>>> d.options["b"]
12
```

### documentation

Documentation defined in the factory initialisation can be accessed from either the
`OptionsFactory` or the `Options` instance via a `doc` property, that gives a `dict`
with the documentation for each option:
```python
>>> D.options_factory.doc["a"]  # Get doc from the factory
'option a'
>>> D.options_factory.doc["b"]  # No doc was defined for this option
>>> d = D()
>>> d.options.doc["f"]  # Get doc from the Options instance
'option f'
```


### `value_type`

The value_type argument can be used to give a type or sequence of types that the option
is allowed to have. Trying to set an option with a non-allowed type raises a
`ValueError`:
```python
>>> d2 = D(d=-2)
ValueError: The value -2 of key=d is not compatible with check_all
>>> d3 = D(f=8)
>>> d3.options.f
8
>>> d4 = D(f=9.5)
>>> d4.options.f
9.5
>>> d5 = D(f="a string")
TypeError: a string is not of type (<class 'int'>, <class 'float'>) for key=f
```


### checking values

There are two ways of checking the values that are set for options.

#### `allowed`

The `allowed` keyword sets a list of allowed options. A `ValueError` is raised if the
value being set is not in the list. `allowed` cannot be set if either of `check_all` or
`check_any` is. Example:
```python
>>> d6 = D(c=2)
ValueError: 2 is not in the allowed values (1, 2, 3) for key=c
>>> d7 = D(c=4)
ValueError: 4 is not in the allowed values (1, 2, 3) for key=c
```

#### `check_all` and `check_any`

These arguments can be passed a list of expressions. The expressions passed to
`check_all` must all evaluate to `True`, or an `ValueError` is raised. At least one of
the expressions passed to `check_any` is raised. The choice of `check_any` or
`check_all` is a matter of convenience and clarity - the effect of either could be
achieved with a single, sufficiently complicated, expression. They can both be set at
the same time, although this probably not often useful. Neither can be set if the
`allowed` keyword is. Example:
```python
>>> d8 = D(d=14)
>>> d8.options.d
14
>>> d9 = D(d=-1)
ValueError: The value -1 of key=d is not compatible with check_all
>>> d10 = D(e=5)
>>> d10.options.e
5
>>> d11 = D(e=6)
ValueError: The value 6 of key=e is not compatible with check_any
>>> d12 = D(g=1)
>>> d12.options.g
1
>>> d13 = D(g=-1)
ValueError: The value -1 of key=g is not compatible with check_all
>>> d14 = D(g=5)
ValueError: The value 5 of key=g is not compatible with check_any
>>> d15 = D(g=9)
>>> d15.options.g
9
>>> d16 = D(g=10)
ValueError: The value 10 of key=g is not compatible with check_all
```

Default expressions
-------------------

Much more flexibility is offered for default values by using expressions. These are
single-argument functions (lambda expressions are often useful), which return the
desired default value when passed an `Options` object, from which the values of other
options (which may or may not be expressions themselves) can be accessed. See the `class
C` example above. When [nested options](#nested_options) are used, expressions can also
access values in subsections or parent sections of the options tree:
```python
from optionsfactory import OptionsFactory


class E:
    options_factory = OptionsFactory(
        a=1,
        b=lambda options: options.a + options.subsection1.c + options.subsection2.e,
        subsection1=OptionsFactory(
            c=lambda options: options.parent.a + options.parent.subsection2.e,
            subsubsection=OptionsFactory(d=2),
        ),
        subsection2=OptionsFactory(
            e=lambda options: options.parent.subsection1.subsubsection.d,
        ),
    )

    def __init__(self, **kwargs):
        self.options = self.options_factory.create(kwargs)
```
If we initialise `E` with just the defaults
```python
>>> e = E()
>>> e.options.a
1
>>> e.options.b
6
>>> e.options.subsection1.c
3
>>> e.options.subsection1.subsubsection.d
2
>>> e.options.subsection2.e
2
```


OptionsFactory extension for subclasses
---------------------------------------

Sometimes it can be useful to create an extended version of an `OptionsFactory`. For
example a child class might have some extra options that are not needed in its parent
class, or might require different default values. The `OptionsFatory.add()` method
creates a new `OptionsFactory` from an existing one, with the keyword arguments adding
to or overriding the options in the original factory. When overriding existing options,
pass a value or expression to keep existing documentation and checks, or a `WithMeta`
object to provide new documentation and checks. Example:
```python
from optionsfactory import OptionsFactory


class Parent:
    options_factory = OptionsFactory(
        a=WithMeta(1, doc="option a"),
        b=WithMeta(2, doc="option b"),
        c=WithMeta(3, doc="option c"),
    )

    def __init__(self, **kwargs):
        self.optiotns = self.options_factory(kwargs)

class Child(Parent):
    options_factory = Parent.options_factory.add(
        # Keep 'a' unchanged
        b=4,  # Change the default value of 'b', but keep the documentation
        c=WithMeta(5, doc="child option c"),  # New default and attributes for 'c'
        d=WithMeta(6, doc="new option d"),  # New option not present in the parent
    )
```
and if we create a `Child` instance
```python
>>> child = Child()
>>> child.options.a
1
>>> child.options.doc["a"]
'option a'
>>> child.options.b
4
>>> child.options.doc["b"]
'option b'
>>> child.options.c
5
>>> child.options.doc["c"]
'child option c'
>>> child.options.d
6
>>> child.options.doc["d"]
'new option d'
```


Nested options
--------------

Nested options are created by passing another `OptionsFactory` as a keyword argument in
the OptionsFactory constructor. See the [nested structure](#nested_structure) example
below.


Collecting defaults
-------------------

It can be useful to collect options from several factories together into a higher-level
factory. For example if a `class Container` contains members of several classes, it
might be useful for the `options_factory` of `Container` to have options for all those
members, but to define the options, defaults, documentation, etc. in the particular
classes. This can be done by passing `OptionsFactory` objects as positional arguments to
the `OptionsFactory` constructor - see the [flat structure](#flat_structure) example
below.

Other Features
--------------

### load from YAML

The user settings can be loaded from a YAML file (if `PyYAML` is available - install the
`optionsfactory[yaml]` variant to ensure this):
```python
>>> with open(filename) as f:
>>>     options = options_factory.create_from_yaml(f)
```


### save to YAML

The options can also be saved to a YAML file, either the non-default values only
```python
>>> with open(filename, 'w') as f:
>>>     options.to_yaml(f)
```
or all values including defaults, by passing `True` to the `with_defaults` argument
```python
>>> with open(filename, 'w') as f:
>>>     options.to_yaml(f, True)  # saves options with default values as well
```


Examples
--------

Here are a couple of more complicated examples of the patterns that `OptionsFactory` was
designed for.


### flat structure

`class A` contains members of types `B` and `C`, so `A.options_factory` collects the
default values, documentation, etc. from `B.options_factory` and `C.options_factory` by
taking them as positional arguments to the constructor. Then the `Options` object of `A`
is used to create the `Options` objects for `B` and `C`, which will have only the
options relevant to themselves in, because `B.options_factory` and `C.options_factory`
ignore any undefined options in the argument passed to `create`.

```python
class A:
    options_factory = OptionsFactory(
        B.options_factory,
        C.options_factory,
        a_opt1 = WithMeta(1, allowed=[1, 3, 7]),
        a_opt2 = WithMeta(2, value_type=[int, float]),
    )

    def __init__(self, user_options):
        self.options = self.options_factory(user_options)
        self.b = B(self.options)
        self.c = C(self.options)

class B:
    options_factory = OptionsFactory(
        b_opt = WithMeta(3.0, checks=is_positive),
    )

    def __init__(self, options):
        self.options = self.options_factory.create(options)

class C:
    options_factory = OptionsFactory(
        c_opt = WithMeta("c-value", value_type=str)
    )

    def __init__(self, options):
        self.options = self.options_factory.create(options)
```

If `B` or `C` were intended to also be used as user-facing classes, which want to get
their options from `**kwargs`, it would also be possible to have
```python
def __init__(self, **kwargs):
    self.options = self.options_factory(kwargs)
```
and create the objects in `A`'s constructor like `self.b = B(**self.options)`.


### nested structure

Similar to the flat structure above, but keeping the options for different member
objects separated in different sections:
```python
class A:
    options_factory = OptionsFactory(
        B=B.options_factory,
        C=C.options_factory,
        a_opt1 = WithMeta(1, allowed=[1, 3, 7]),
        a_opt2 = WithMeta(2, value_type=[int, float]),
    )

    def __init__(self, user_options):
        self.options = self.options_factory(user_options)
        self.b = B(self.options.B)
        self.c = C(self.options.C)

class B:
    options_factory = OptionsFactory(
        b_opt = WithMeta(3.0, checks=is_positive),
    )

    def __init__(self, options):
        self.options = options

class C:
    options_factory = OptionsFactory(
        c_opt = WithMeta("c-value", value_type=str)
    )

    def __init__(self, options):
        self.options = options
```

If `A` needs to change the default options for one of the nested sections, can use the
`add()` method like `B={"b_opt": 7.0)`.

Default expressions in a nested options structure can use values from sub-sections, or
from parent sections, see [Default expressions](#default_expressions).

If `B` or `C` should be allowed to be created independently of a containing class like
`A`, then you can instead define the constructor as
```python
class B:
    options_factory = OptionsFactory(
        b_opt = WithMeta(3.0, checks=is_positive),
    )

    def __init__(self, options):
        self.options = self.options_factory(options)
```
This will have the same effect as the above code when called with `self.b =
B(self.options.B)` but also allows creating a `B` like `another_b = B({"b_opt": 4.0})`.
(This version will be slightly more expensive than the one above because the `Options`
object will be converted to a `dict`-like iterable and a new `Options` created by
parsing that iterable.)


### global options

Not recommended, but you could create a global options object for your package/program.
For example in a file `mypackage.py`
```python
from optionsfactory import OptionsFactory


global_options = None


options_factory = OptionsFactory(
    opt1 = 1,
    opt2 = 2,
)


def setup(input_options):
    global global_options
    global_options = options_factory.create(input_options)
```

MutableOptionsFactory
=====================

`MutableOptionsFactory` is almost identical to `OptionsFactory`, but creates
`MutableOptions` objects which can be modified after being created (it also has a
`create_immutable()` method, equivalent to `OptionsFactory.create()` to create
`Options` objects). `MutableOptions` behave like `Options` with the exception that
values can be set, or reset to the default value (using `del`) after the object is
created. Default values are re-calculated if any option is changed. Example:
```python
>>> from options_factory import MutableOptionsFactory
>>> factory = MutableOptionsFactory(a=1, b=lambda options: 2.0*options.a)
>>> mutable_options = factory.create({"a": 3, "b": 4})
>>> mutable_options.a
3
>>> mutable_options.b
4
>>> del mutable_options.b
>>> mutable_options.b
6.0
>>> mutable_options.a = 5
>>> mutable_options.b
10.0
>>> mutable_options["a"] = 7.5
>>> mutable_options.b
15.0
>>> del mutable_options["a"]
>>> mutable_options.b
2.0
>>> mutable_options.a
1
```


Expressions for non-default values
==================================

Passing expressions for non-default values should work, although it has not been tested
yet. Expressions cannot at present be loaded from YAML files.


Acknowledgements
================

Thanks to [Ben Dudson](https://github.com/bendudson) and [Peter
Hill](https://github.com/ZedThree) for discussion on options handling in the [hypnotoad
project](https://github.com/boutproject/hypnotoad/pull/33) and ideas in
[frozen_options](https://github.com/bendudson/frozen-options).
