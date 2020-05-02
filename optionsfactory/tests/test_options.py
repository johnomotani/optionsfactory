import pytest

from ..optionsfactory import OptionsFactory, WithMeta
from ..checks import is_positive


class TestOptions:
    def test_defaults(self):
        factory = OptionsFactory(
            a=1,
            b=lambda options: options.a,
            c=lambda options: options["a"],
            d=lambda options: options.e + options.c,
            e=WithMeta(2.0, doc="option e", value_type=float, allowed=[2.0, 3.0]),
            f=WithMeta(
                11,
                doc="option f",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
            g=WithMeta(
                lambda options: options.a + 2,
                doc="option g",
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
        assert opts.e == 2.0
        assert opts.f == 11
        assert opts.g == 3

        assert opts["a"] == 1
        assert opts["b"] == 1
        assert opts["c"] == 1
        assert opts["d"] == 3.0
        assert opts["e"] == 2.0
        assert opts["f"] == 11
        assert opts["g"] == 3

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
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert "c" in opts
        assert "d" in opts
        assert "e" in opts
        assert "f" in opts
        assert "g" in opts
        assert not ("x" in opts)

        assert len(opts) == 7
        assert sorted([k for k in opts]) == sorted(["a", "b", "c", "d", "e", "f", "g"])
        assert sorted(opts.values()) == sorted([1, 1, 1, 3.0, 2.0, 11, 3])
        assert sorted(opts.items()) == sorted(
            [("a", 1), ("b", 1), ("c", 1), ("d", 3.0), ("e", 2.0), ("f", 11), ("g", 3)]
        )

    def test_initialise(self):
        factory = OptionsFactory(
            a=1,
            b=lambda options: options.a,
            c=lambda options: options["a"],
            d=lambda options: options.b + options.c,
            e=WithMeta(2.0, doc="option e", value_type=float, allowed=[2.0, 3.0]),
            f=WithMeta(
                11,
                doc="option f",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
            g=WithMeta(
                lambda options: options.a + 2,
                doc="option g",
                value_type=int,
                checks=[is_positive, lambda x: x < 20],
            ),
        )

        # test default values
        opts = factory.create({"a": 4, "b": 5, "e": 3.0, "f": 13, "z": 17})

        assert opts.a == 4
        assert opts.b == 5
        assert opts.c == 4
        assert opts.d == 9
        assert opts.e == 3.0
        assert opts.f == 13
        assert opts.g == 6

        # "z" should have been ignored
        with pytest.raises(AttributeError):
            opts.z

        assert opts["a"] == 4
        assert opts["b"] == 5
        assert opts["c"] == 4
        assert opts["d"] == 9
        assert opts["e"] == 3.0
        assert opts["f"] == 13
        assert opts["g"] == 6

        # "z" should have been ignored
        with pytest.raises(KeyError):
            opts["z"]

        with pytest.raises(TypeError):
            opts.a = 2

        with pytest.raises(TypeError):
            opts["a"] = 2

        assert not opts.is_default("a")
        assert not opts.is_default("b")
        assert opts.is_default("c")
        assert opts.is_default("d")
        assert not opts.is_default("e")
        assert not opts.is_default("f")
        assert opts.is_default("g")
        with pytest.raises(KeyError):
            opts.is_default("x")

        assert "a" in opts
        assert "b" in opts
        assert "c" in opts
        assert "d" in opts
        assert "e" in opts
        assert "f" in opts
        assert "g" in opts
        assert not ("x" in opts)

        assert len(opts) == 7
        assert sorted([k for k in opts]) == sorted(["a", "b", "c", "d", "e", "f", "g"])
        assert sorted(opts.values()) == sorted([4, 5, 4, 9, 3.0, 13, 6])
        assert sorted(opts.items()) == sorted(
            [("a", 4), ("b", 5), ("c", 4), ("d", 9), ("e", 3.0), ("f", 13), ("g", 6)]
        )

        with pytest.raises(ValueError):
            opts = factory.create({"e": 2.5})
        with pytest.raises(TypeError):
            opts = factory.create({"e": "2.0"})
        with pytest.raises(TypeError):
            opts = factory.create({"e": 2})
        with pytest.raises(ValueError):
            opts = factory.create({"f": -1})
        with pytest.raises(ValueError):
            opts = factory.create({"f": 30})
        with pytest.raises(TypeError):
            opts = factory.create({"f": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create({"g": -7})
        with pytest.raises(ValueError):
            opts = factory.create({"g": 21})
        with pytest.raises(TypeError):
            opts = factory.create({"g": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create({"a": -7})
        with pytest.raises(ValueError):
            opts = factory.create({"a": 21})
        with pytest.raises(TypeError):
            opts = factory.create({"a": 3.5})

    def test_circular(self):
        factory = OptionsFactory(
            a=lambda options: options.b, b=lambda options: options.a,
        )
        with pytest.raises(ValueError, match="Circular definition"):
            opts = factory.create()

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
