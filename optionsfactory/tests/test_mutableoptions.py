import pytest

from ..optionsfactory import MutableOptionsFactory, WithMeta
from ..checks import is_positive

from .test_options import as_table_test_str


class TestOptions:
    def test_defaults(self):
        factory = MutableOptionsFactory(
            a=1,
            b=lambda options: options.a,
            c=lambda options: options["a"],
            d=lambda options: options.f + options.c,
            e=WithMeta("b", value_type=int),
            f=WithMeta(2.0, doc="option f", value_type=float, allowed=[2.0, 3.0]),
            g=WithMeta(
                11,
                doc="option g",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
        )

        # test default values
        opts = factory.create()

        assert opts.a == 1
        assert opts.b == 1
        assert opts.c == 1
        assert opts.d == 3.0
        assert opts.e == 1
        assert opts.f == 2.0
        assert opts.g == 11
        assert opts.h == 3

        assert opts["a"] == 1
        assert opts["b"] == 1
        assert opts["c"] == 1
        assert opts["d"] == 3.0
        assert opts["e"] == 1
        assert opts["f"] == 2.0
        assert opts["g"] == 11
        assert opts["h"] == 3

        assert opts.doc["a"] is None
        assert opts.doc["b"] is None
        assert opts.doc["c"] is None
        assert opts.doc["d"] is None
        assert opts.doc["e"] is None
        assert opts.doc["f"] == "option f"
        assert opts.doc["g"] == "option g"
        assert opts.doc["h"] == "option h"

        opts.a = 2

        assert opts.a == 2
        assert opts.b == 2
        assert opts.c == 2
        assert opts.d == 4.0
        assert opts.e == 2
        assert opts.f == 2.0
        assert opts.g == 11
        assert opts.h == 4

        assert opts["a"] == 2
        assert opts["b"] == 2
        assert opts["c"] == 2
        assert opts["d"] == 4.0
        assert opts["e"] == 2
        assert opts["f"] == 2.0
        assert opts["g"] == 11
        assert opts["h"] == 4

        assert opts.doc["a"] is None
        assert opts.doc["b"] is None
        assert opts.doc["c"] is None
        assert opts.doc["d"] is None
        assert opts.doc["e"] is None
        assert opts.doc["f"] == "option f"
        assert opts.doc["g"] == "option g"
        assert opts.doc["h"] == "option h"

        # Reset "a" to default
        del opts.a
        assert opts.a == 1
        assert opts.b == 1
        assert opts.c == 1
        assert opts.d == 3.0
        assert opts.e == 1
        assert opts.f == 2.0
        assert opts.g == 11
        assert opts.h == 3

        assert opts.doc["a"] is None
        assert opts.doc["b"] is None
        assert opts.doc["c"] is None
        assert opts.doc["d"] is None
        assert opts.doc["e"] is None
        assert opts.doc["f"] == "option f"
        assert opts.doc["g"] == "option g"
        assert opts.doc["h"] == "option h"

        opts["a"] = 3

        assert opts.a == 3
        assert opts.b == 3
        assert opts.c == 3
        assert opts.d == 5.0
        assert opts.e == 3
        assert opts.f == 2.0
        assert opts.g == 11
        assert opts.h == 5

        assert opts["a"] == 3
        assert opts["b"] == 3
        assert opts["c"] == 3
        assert opts["d"] == 5.0
        assert opts["e"] == 3
        assert opts["f"] == 2.0
        assert opts["g"] == 11
        assert opts["h"] == 5

        assert not opts.is_default("a")
        assert opts.is_default("b")
        assert opts.is_default("c")
        assert opts.is_default("d")
        assert opts.is_default("e")
        assert opts.is_default("f")
        assert opts.is_default("g")
        assert opts.is_default("h")
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert "c" in opts
        assert "d" in opts
        assert "e" in opts
        assert "f" in opts
        assert "g" in opts
        assert "h" in opts
        assert not ("x" in opts)

        assert len(opts) == 8
        assert sorted([k for k in opts]) == sorted(
            ["a", "b", "c", "d", "e", "f", "g", "h"]
        )
        assert sorted(opts.values()) == sorted([3, 3, 3, 5.0, 3, 2.0, 11, 5])
        assert sorted(opts.items()) == sorted(
            [
                ("a", 3),
                ("b", 3),
                ("c", 3),
                ("d", 5.0),
                ("e", 3),
                ("f", 2.0),
                ("g", 11),
                ("h", 5),
            ]
        )

        # Reset "a" to default
        del opts["a"]
        assert opts.a == 1
        assert opts.b == 1
        assert opts.c == 1
        assert opts.d == 3.0
        assert opts.e == 1
        assert opts.f == 2.0
        assert opts.g == 11
        assert opts.h == 3

    def test_initialise(self):
        factory = MutableOptionsFactory(
            a=1,
            b=lambda options: options.a,
            c=lambda options: options["a"],
            d=lambda options: options.b + options.c,
            e=WithMeta("b", value_type=int),
            f=WithMeta(2.0, doc="option f", value_type=float, allowed=[2.0, 3.0]),
            g=WithMeta(
                11,
                doc="option g",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
        )

        # test default values
        opts = factory.create({"a": 4, "b": 5, "f": 3.0, "g": 13, "z": 17})

        assert opts.a == 4
        assert opts.b == 5
        assert opts.c == 4
        assert opts.d == 9
        assert opts.e == 5
        assert opts.f == 3.0
        assert opts.g == 13
        assert opts.h == 6

        # "z" should have been ignored
        with pytest.raises(AttributeError):
            opts.z

        assert opts["a"] == 4
        assert opts["b"] == 5
        assert opts["c"] == 4
        assert opts["d"] == 9
        assert opts["e"] == 5
        assert opts["f"] == 3.0
        assert opts["g"] == 13
        assert opts["h"] == 6

        # "z" should have been ignored
        with pytest.raises(KeyError):
            opts["z"]

        assert opts.doc["a"] is None
        assert opts.doc["b"] is None
        assert opts.doc["c"] is None
        assert opts.doc["d"] is None
        assert opts.doc["e"] is None
        assert opts.doc["f"] == "option f"
        assert opts.doc["g"] == "option g"
        assert opts.doc["h"] == "option h"

        opts.a = 2

        assert opts.a == 2
        assert opts.b == 5
        assert opts.c == 2
        assert opts.d == 7
        assert opts.e == 5
        assert opts.f == 3.0
        assert opts.g == 13
        assert opts.h == 4

        assert opts.doc["a"] is None
        assert opts.doc["b"] is None
        assert opts.doc["c"] is None
        assert opts.doc["d"] is None
        assert opts.doc["e"] is None
        assert opts.doc["f"] == "option f"
        assert opts.doc["g"] == "option g"
        assert opts.doc["h"] == "option h"

        opts["a"] = 3

        assert opts.a == 3
        assert opts.b == 5
        assert opts.c == 3
        assert opts.d == 8
        assert opts.e == 5
        assert opts.f == 3.0
        assert opts.g == 13
        assert opts.h == 5

        assert not opts.is_default("a")
        assert not opts.is_default("b")
        assert opts.is_default("c")
        assert opts.is_default("d")
        assert opts.is_default("e")
        assert not opts.is_default("f")
        assert not opts.is_default("g")
        assert opts.is_default("h")
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert "c" in opts
        assert "d" in opts
        assert "e" in opts
        assert "f" in opts
        assert "g" in opts
        assert "h" in opts
        assert not ("x" in opts)

        assert len(opts) == 8
        assert sorted([k for k in opts]) == sorted(
            ["a", "b", "c", "d", "e", "f", "g", "h"]
        )
        assert sorted(opts.values()) == sorted([3, 5, 3, 8, 5, 3.0, 13, 5])
        assert sorted(opts.items()) == sorted(
            [
                ("a", 3),
                ("b", 5),
                ("c", 3),
                ("d", 8),
                ("e", 5),
                ("f", 3.0),
                ("g", 13),
                ("h", 5),
            ]
        )

        with pytest.raises(ValueError):
            opts = factory.create({"f": 2.5})
        with pytest.raises(TypeError):
            opts = factory.create({"f": "2.0"})
        with pytest.raises(TypeError):
            opts = factory.create({"f": 2})
        with pytest.raises(ValueError):
            opts = factory.create({"g": -1})
        with pytest.raises(ValueError):
            opts = factory.create({"g": 30})
        with pytest.raises(TypeError):
            opts = factory.create({"g": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create({"h": -7})
        with pytest.raises(ValueError):
            opts = factory.create({"h": 21})
        with pytest.raises(TypeError):
            opts = factory.create({"h": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create({"a": -7})
            opts.h
        with pytest.raises(ValueError):
            opts = factory.create({"a": 21})
            opts.h
        with pytest.raises(TypeError):
            opts = factory.create({"a": 3.5})
            opts.h

    def test_circular(self):
        factory = MutableOptionsFactory(
            a=lambda options: options.b, b=lambda options: options.a,
        )
        opts = factory.create()
        with pytest.raises(ValueError, match="Circular definition"):
            opts.a

        opts = factory.create({"b": 3})
        assert opts.a == 3
        assert opts.b == 3

        assert opts.is_default("a")
        assert not opts.is_default("b")
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert not ("x" in opts)

        assert len(opts) == 2
        assert sorted([k for k in opts]) == sorted(["a", "b"])
        assert sorted(opts.values()) == sorted([3, 3])
        assert sorted(opts.items()) == sorted([("a", 3), ("b", 3)])

        del opts.b
        with pytest.raises(ValueError, match="Circular definition"):
            opts.b

    def test_as_table(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create({"b": 3})
        assert opts.as_table() == as_table_test_str

    def test_str(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create({"b": 3})
        assert str(opts) == "{a: 1 (default), b: 3}"

        del opts.b
        opts.a = 4
        assert str(opts) == "{a: 4, b: 2 (default)}"


class TestMutableOptionsFactoryImmutable:
    def test_defaults(self):
        factory = MutableOptionsFactory(
            a=1,
            b=lambda options: options.a,
            c=lambda options: options["a"],
            d=lambda options: options.f + options.c,
            e=WithMeta("b", value_type=int),
            f=WithMeta(2.0, doc="option f", value_type=float, allowed=[2.0, 3.0]),
            g=WithMeta(
                11,
                doc="option g",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
        )

        # test default values
        opts = factory.create_immutable()

        assert opts.a == 1
        assert opts.b == 1
        assert opts.c == 1
        assert opts.d == 3.0
        assert opts.e == 1
        assert opts.f == 2.0
        assert opts.g == 11
        assert opts.h == 3

        assert opts["a"] == 1
        assert opts["b"] == 1
        assert opts["c"] == 1
        assert opts["d"] == 3.0
        assert opts["e"] == 1
        assert opts["f"] == 2.0
        assert opts["g"] == 11
        assert opts["h"] == 3

        assert opts.doc["a"] is None
        assert opts.doc["b"] is None
        assert opts.doc["c"] is None
        assert opts.doc["d"] is None
        assert opts.doc["e"] is None
        assert opts.doc["f"] == "option f"
        assert opts.doc["g"] == "option g"
        assert opts.doc["h"] == "option h"

        with pytest.raises(TypeError):
            opts.a = 2

        with pytest.raises(TypeError):
            opts["a"] = 2

        assert opts.is_default("a")
        assert opts.is_default("b")
        assert opts.is_default("c")
        assert opts.is_default("d")
        assert opts.is_default("e")
        assert opts.is_default("f")
        assert opts.is_default("g")
        assert opts.is_default("h")
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert "c" in opts
        assert "d" in opts
        assert "e" in opts
        assert "f" in opts
        assert "g" in opts
        assert "h" in opts
        assert not ("x" in opts)

        assert len(opts) == 8
        assert sorted([k for k in opts]) == sorted(
            ["a", "b", "c", "d", "e", "f", "g", "h"]
        )
        assert sorted(opts.values()) == sorted([1, 1, 1, 3.0, 1, 2.0, 11, 3])
        assert sorted(opts.items()) == sorted(
            [
                ("a", 1),
                ("b", 1),
                ("c", 1),
                ("d", 3.0),
                ("e", 1),
                ("f", 2.0),
                ("g", 11),
                ("h", 3),
            ]
        )

    def test_initialise(self):
        factory = MutableOptionsFactory(
            a=1,
            b=lambda options: options.a,
            c=lambda options: options["a"],
            d=lambda options: options.b + options.c,
            e=WithMeta("b", value_type=int),
            f=WithMeta(2.0, doc="option f", value_type=float, allowed=[2.0, 3.0]),
            g=WithMeta(
                11,
                doc="option g",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
        )

        # test default values
        opts = factory.create_immutable({"a": 4, "b": 5, "f": 3.0, "g": 13, "z": 17})

        assert opts.a == 4
        assert opts.b == 5
        assert opts.c == 4
        assert opts.d == 9
        assert opts.e == 5
        assert opts.f == 3.0
        assert opts.g == 13
        assert opts.h == 6

        # "z" should have been ignored
        with pytest.raises(AttributeError):
            opts.z

        assert opts["a"] == 4
        assert opts["b"] == 5
        assert opts["c"] == 4
        assert opts["d"] == 9
        assert opts["e"] == 5
        assert opts["f"] == 3.0
        assert opts["g"] == 13
        assert opts["h"] == 6

        # "z" should have been ignored
        with pytest.raises(KeyError):
            opts["z"]

        assert opts.doc["a"] is None
        assert opts.doc["b"] is None
        assert opts.doc["c"] is None
        assert opts.doc["d"] is None
        assert opts.doc["e"] is None
        assert opts.doc["f"] == "option f"
        assert opts.doc["g"] == "option g"
        assert opts.doc["h"] == "option h"

        with pytest.raises(TypeError):
            opts.a = 2

        with pytest.raises(TypeError):
            opts["a"] = 2

        assert not opts.is_default("a")
        assert not opts.is_default("b")
        assert opts.is_default("c")
        assert opts.is_default("d")
        assert opts.is_default("e")
        assert not opts.is_default("f")
        assert not opts.is_default("g")
        assert opts.is_default("h")
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert "c" in opts
        assert "d" in opts
        assert "e" in opts
        assert "f" in opts
        assert "g" in opts
        assert "h" in opts
        assert not ("x" in opts)

        assert len(opts) == 8
        assert sorted([k for k in opts]) == sorted(
            ["a", "b", "c", "d", "e", "f", "g", "h"]
        )
        assert sorted(opts.values()) == sorted([4, 5, 4, 9, 5, 3.0, 13, 6])
        assert sorted(opts.items()) == sorted(
            [
                ("a", 4),
                ("b", 5),
                ("c", 4),
                ("d", 9),
                ("e", 5),
                ("f", 3.0),
                ("g", 13),
                ("h", 6),
            ]
        )

        with pytest.raises(ValueError):
            opts = factory.create_immutable({"f": 2.5})
        with pytest.raises(TypeError):
            opts = factory.create_immutable({"f": "2.0"})
        with pytest.raises(TypeError):
            opts = factory.create_immutable({"f": 2})
        with pytest.raises(ValueError):
            opts = factory.create_immutable({"g": -1})
        with pytest.raises(ValueError):
            opts = factory.create_immutable({"g": 30})
        with pytest.raises(TypeError):
            opts = factory.create_immutable({"g": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create_immutable({"h": -7})
        with pytest.raises(ValueError):
            opts = factory.create_immutable({"h": 21})
        with pytest.raises(TypeError):
            opts = factory.create_immutable({"h": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create_immutable({"a": -7})
        with pytest.raises(ValueError):
            opts = factory.create_immutable({"a": 21})
        with pytest.raises(TypeError):
            opts = factory.create_immutable({"a": 3.5})

    def test_circular(self):
        factory = MutableOptionsFactory(
            a=lambda options: options.b, b=lambda options: options.a,
        )
        with pytest.raises(ValueError, match="Circular definition"):
            opts = factory.create_immutable()

        opts = factory.create_immutable({"b": 3})
        assert opts.a == 3
        assert opts.b == 3

        assert opts.is_default("a")
        assert not opts.is_default("b")
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert not ("x" in opts)

        assert len(opts) == 2
        assert sorted([k for k in opts]) == sorted(["a", "b"])
        assert sorted(opts.values()) == sorted([3, 3])
        assert sorted(opts.items()) == sorted([("a", 3), ("b", 3)])

    def test_as_table(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create_immutable({"b": 3})
        assert opts.as_table() == as_table_test_str

    def test_str(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create_immutable({"b": 3})
        assert str(opts) == "{a: 1 (default), b: 3}"
