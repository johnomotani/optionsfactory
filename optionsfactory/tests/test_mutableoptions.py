import pytest

from io import StringIO

from ..optionsfactory import MutableOptionsFactory, WithMeta
from ..checks import is_positive

from .test_options import as_table_test_str, as_table_test_str_nested


class TestMutableOptions:
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
                check_all=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                check_any=[is_positive, lambda x: x < -20],
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

        assert factory.doc["a"] is None
        assert factory.doc["b"] is None
        assert factory.doc["c"] is None
        assert factory.doc["d"] is None
        assert factory.doc["e"] is None
        assert factory.doc["f"] == "option f"
        assert factory.doc["g"] == "option g"
        assert factory.doc["h"] == "option h"

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
                check_all=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                check_any=[is_positive, lambda x: x < -20],
            ),
        )

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
        assert factory.create({"h": -21}).h == -21
        with pytest.raises(TypeError):
            opts = factory.create({"h": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create({"a": -7})
            opts.h
        opts = factory.create({"a": -23})
        assert opts.h == -21
        with pytest.raises(TypeError):
            opts = factory.create({"a": 3.5})
            opts.h

    def test_initialise_from_options(self):
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
                check_all=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                check_any=[is_positive, lambda x: x < -20],
            ),
        )

        opts1 = factory.create({"a": 4, "b": 5, "f": 3.0, "g": 13, "z": 17})

        opts2 = factory.create(opts1)

        assert dict(opts1) == dict(opts2)

        opts3 = factory.create_immutable(opts1)

        assert dict(opts1) == dict(opts3)

    def test_nested_from_parent(self):
        factory = MutableOptionsFactory(
            a=1,
            subsection=MutableOptionsFactory(
                b=2, c=lambda options: options.b + options.parent.a
            ),
        )

        opts = factory.create({})

        assert opts.a == 1
        assert opts.subsection.b == 2
        assert opts.subsection.c == 3

        opts.a = 6

        assert opts.a == 6
        assert opts.subsection.b == 2
        assert opts.subsection.c == 8

        opts2 = factory.create({"a": 4})

        assert opts2.a == 4
        assert opts2.subsection.b == 2
        assert opts2.subsection.c == 6

    def test_values_nested(self):
        factory = MutableOptionsFactory(a=1, subsection=MutableOptionsFactory(b=2), c=3)
        opts = factory.create({})
        values_iter = opts.values()
        assert next(values_iter) == 1
        value = next(values_iter)
        assert isinstance(value, MutableOptionsFactory.MutableOptions)
        assert dict(value) == {"b": 2}
        assert next(values_iter) == 3

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

    def test_add_defaults(self):
        subfactory = MutableOptionsFactory(
            d=WithMeta(4, doc="option d1"),
            e=WithMeta(5, doc="option e1"),
            f=WithMeta(6, doc="option f1"),
        )
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a1"),
            b=WithMeta(2, doc="option b1"),
            c=WithMeta(3, doc="option c1"),
            subsection=subfactory,
        )

        factory2 = factory.add(
            b=12,
            c=WithMeta(13, doc="option c2"),
            g=17,
            subsection={"d": 14, "e": WithMeta(15, doc="option e2"), "h": 18},
            subsection2=MutableOptionsFactory(i=WithMeta(19, doc="option i2")),
        )

        opts = factory2.create({})

        assert opts.a == 1
        assert opts.b == 12
        assert opts.c == 13
        assert opts.subsection.d == 14
        assert opts.subsection.e == 15
        assert opts.subsection.f == 6
        assert opts.g == 17
        assert opts.subsection.h == 18
        assert opts.subsection2.i == 19

        assert opts.doc["a"] == "option a1"
        assert opts.doc["b"] == "option b1"
        assert opts.doc["c"] == "option c2"
        assert opts.doc["subsection"]["d"] == "option d1"
        assert opts.doc["subsection"]["e"] == "option e2"
        assert opts.doc["subsection"]["f"] == "option f1"
        assert opts.doc["g"] is None
        assert opts.doc["subsection"]["h"] is None
        assert opts.doc["subsection2"]["i"] == "option i2"

        with pytest.raises(ValueError, match="Passing an OptionsFactory"):
            factory.add(a=MutableOptionsFactory(j=2))

        with pytest.raises(ValueError, match="Updating the section"):
            factory.add(subsection=MutableOptionsFactory(d=14, e=15, f=16))

    def test_add_initialise(self):
        subfactory = MutableOptionsFactory(
            d=WithMeta(4, doc="option d1"),
            e=WithMeta(5, doc="option e1"),
            f=WithMeta(6, doc="option f1"),
        )
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a1"),
            b=WithMeta(2, doc="option b1"),
            c=WithMeta(3, doc="option c1"),
            subsection=subfactory,
        )

        factory2 = factory.add(
            b=12,
            c=WithMeta(13, doc="option c2"),
            g=17,
            subsection={"d": 14, "e": WithMeta(15, doc="option e2"), "h": 18},
            subsection2=MutableOptionsFactory(i=WithMeta(19, doc="option i2")),
        )

        opts = factory2.create(
            {
                "a": 21,
                "b": 22,
                "c": 23,
                "subsection": {"d": 24, "e": 25, "f": 26, "h": 27},
                "g": 28,
                "subsection2": {"i": 29},
            }
        )

        assert opts.a == 21
        assert opts.b == 22
        assert opts.c == 23
        assert opts.subsection.d == 24
        assert opts.subsection.e == 25
        assert opts.subsection.f == 26
        assert opts.g == 28
        assert opts.subsection.h == 27
        assert opts.subsection2.i == 29

        assert opts.doc["a"] == "option a1"
        assert opts.doc["b"] == "option b1"
        assert opts.doc["c"] == "option c2"
        assert opts.doc["subsection"]["d"] == "option d1"
        assert opts.doc["subsection"]["e"] == "option e2"
        assert opts.doc["subsection"]["f"] == "option f1"
        assert opts.doc["g"] is None
        assert opts.doc["subsection"]["h"] is None
        assert opts.doc["subsection2"]["i"] == "option i2"

        with pytest.raises(ValueError, match="Passing an OptionsFactory"):
            factory.add(a=MutableOptionsFactory(j=2))

        with pytest.raises(ValueError, match="Updating the section"):
            factory.add(subsection=MutableOptionsFactory(d=14, e=15, f=16))

    def test_as_table(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create({"b": 3})
        assert opts.as_table() == as_table_test_str

    def test_as_table_nested(self):
        factory = MutableOptionsFactory(
            a=1,
            b=2,
            subsection1=MutableOptionsFactory(
                c=4, subsubsection=MutableOptionsFactory(d=5)
            ),
            subsection2=MutableOptionsFactory(e=6),
        )
        opts = factory.create({"b": 3})
        assert opts.as_table() == as_table_test_str_nested

    def test_str(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create({"b": 3})
        assert str(opts) == "{a: 1 (default), b: 3}"

        del opts.b
        opts.a = 4
        assert str(opts) == "{a: 4, b: 2 (default)}"

    def test_str_nested(self):
        factory = MutableOptionsFactory(
            a=1,
            subsection=MutableOptionsFactory(
                c=3, subsubsection=MutableOptionsFactory(d=4)
            ),
            b=2,
        )
        opts = factory.create({"b": 5, "subsection": {"subsubsection": {"d": 6}}})
        assert (
            str(opts)
            == "{a: 1 (default), subsection: {c: 3 (default), subsubsection: {d: 6}}, "
            "b: 5}"
        )

    def test_create_from_yaml(self):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(a=1, b=2)

        with StringIO() as f:
            f.write("a: 3\nc: 4")

            # reset to beginning of f
            f.seek(0)

            opts = factory.create_from_yaml(f)

        assert opts.a == 3
        assert opts.b == 2

        opts.a = 5
        assert opts.a == 5

    def test_create_from_yaml_nested(self):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(
            a=1,
            b=2,
            subsection=MutableOptionsFactory(
                c=3, subsubsection=MutableOptionsFactory(d=4)
            ),
            e=5,
        )

        with StringIO() as f:
            f.write(
                "a: 11\ne: 15\nsubsection:\n  c: 13\n  subsubsection:\n    d: 14\nb: 12"
            )

            # reset to beginning of f
            f.seek(0)

            opts = factory.create_from_yaml(f)

        assert opts.a == 11
        assert opts.b == 12
        assert opts.subsection.c == 13
        assert opts.subsection.subsubsection.d == 14
        assert opts.e == 15

        opts.a = 5
        assert opts.a == 5

    def test_to_yaml(self):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create({"a": 3})

        # file_like=None argument makes yaml.dump() return the YAML as a string
        assert opts.to_yaml(None) == "a: 3\n"
        assert opts.to_yaml(None, True) == "a: 3\nb: 2\n"

    def test_to_yaml_nested(self):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(
            a=1,
            b=2,
            subsection=MutableOptionsFactory(
                c=3, subsubsection=MutableOptionsFactory(d=4)
            ),
            e=5,
        )

        opts = factory.create(
            {"a": 11, "subsection": {"c": 13, "subsubsection": {"d": 14}}}
        )

        assert (
            opts.to_yaml(None)
            == "a: 11\nsubsection:\n  c: 13\n  subsubsection:\n    d: 14\n"
        )

        assert (
            opts.to_yaml(None, True)
            == "a: 11\nb: 2\ne: 5\nsubsection:\n  c: 13\n  subsubsection:\n    d: 14\n"
        )

    def test_nested_defaults(self):
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a"),
            b=lambda options: options.subsection1.c
            + options.subsection2.subsubsection.f,
            subsection1=MutableOptionsFactory(c=WithMeta(3, doc="option 1c"), d=4),
            subsection2=MutableOptionsFactory(
                c=WithMeta(5, doc="option 2c"),
                e=6,
                subsubsection=MutableOptionsFactory(f=WithMeta(7, doc="option f")),
            ),
        )

        opts = factory.create({})

        assert opts.a == 1
        assert opts.b == 10
        assert opts.subsection1.c == 3
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 7

        opts.subsection2.subsubsection.f = 8

        assert opts.a == 1
        assert opts.b == 11
        assert opts.subsection1.c == 3
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 8

        assert opts.doc["a"] == "option a"
        assert opts.doc["b"] is None
        assert opts.doc["subsection1"]["c"] == "option 1c"
        assert opts.subsection1.doc["c"] == "option 1c"
        assert opts.doc["subsection1"]["d"] is None
        assert opts.doc["subsection2"]["c"] == "option 2c"
        assert opts.subsection2.doc["c"] == "option 2c"
        assert opts.doc["subsection2"]["e"] is None
        assert opts.subsection2.subsubsection.doc["f"] == "option f"

    def test_nested_initialise(self):
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a"),
            b=lambda options: options.subsection1.c
            + options.subsection2.subsubsection.f,
            subsection1=MutableOptionsFactory(c=WithMeta(3, doc="option 1c"), d=4),
            subsection2=MutableOptionsFactory(
                c=WithMeta(5, doc="option 2c"),
                e=6,
                subsubsection=MutableOptionsFactory(f=WithMeta(7, doc="option f")),
            ),
        )

        opts = factory.create(
            {
                "a": 2,
                "subsection1": {"c": 7},
                "subsection2": {"subsubsection": {"f": 8}},
            }
        )

        assert opts.a == 2
        assert opts.b == 15
        assert opts.subsection1.c == 7
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 8

        opts.subsection2.subsubsection.f = 9

        assert opts.a == 2
        assert opts.b == 16
        assert opts.subsection1.c == 7
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 9

        assert opts.doc["a"] == "option a"
        assert opts.doc["b"] is None
        assert opts.doc["subsection1"]["c"] == "option 1c"
        assert opts.subsection1.doc["c"] == "option 1c"
        assert opts.doc["subsection1"]["d"] is None
        assert opts.doc["subsection2"]["c"] == "option 2c"
        assert opts.subsection2.doc["c"] == "option 2c"
        assert opts.doc["subsection2"]["e"] is None
        assert opts.subsection2.subsubsection.doc["f"] == "option f"

    def test_nested_with_arg_initialise(self):
        factory2 = MutableOptionsFactory(
            x=WithMeta(11, doc="option x"),
            y=12,
            subsection3=MutableOptionsFactory(z=WithMeta(13, doc="option z")),
        )

        factory = MutableOptionsFactory(
            factory2,
            a=WithMeta(1, doc="option a"),
            b=lambda options: options.subsection1.c
            + options.subsection2.subsubsection.f
            + options.subsection3.z,
            subsection1=MutableOptionsFactory(c=WithMeta(3, doc="option 1c"), d=4),
            subsection2=MutableOptionsFactory(
                c=WithMeta(5, doc="option 2c"),
                e=6,
                subsubsection=MutableOptionsFactory(f=WithMeta(7, doc="option f")),
            ),
        )

        opts = factory.create(
            {
                "a": 2,
                "x": 21,
                "subsection1": {"c": 7},
                "subsection2": {"subsubsection": {"f": 8}},
                "subsection3": {"z": 23},
            }
        )

        assert opts.a == 2
        assert opts.b == 38
        assert opts.x == 21
        assert opts.subsection1.c == 7
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 8
        assert opts.subsection3.z == 23

        assert opts.doc["a"] == "option a"
        assert opts.doc["b"] is None
        assert opts.doc["x"] == "option x"
        assert opts.doc["subsection1"]["c"] == "option 1c"
        assert opts.subsection1.doc["c"] == "option 1c"
        assert opts.doc["subsection1"]["d"] is None
        assert opts.doc["subsection2"]["c"] == "option 2c"
        assert opts.subsection2.doc["c"] == "option 2c"
        assert opts.doc["subsection2"]["e"] is None
        assert opts.subsection2.subsubsection.doc["f"] == "option f"
        assert opts.subsection3.doc["z"] == "option z"

        opts.a = 30
        opts.subsection3.z = 42

        assert opts.a == 30
        assert opts.b == 57
        assert opts.x == 21
        assert opts.subsection1.c == 7
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 8
        assert opts.subsection3.z == 42

        assert opts.doc["a"] == "option a"
        assert opts.doc["b"] is None
        assert opts.doc["x"] == "option x"
        assert opts.doc["subsection1"]["c"] == "option 1c"
        assert opts.subsection1.doc["c"] == "option 1c"
        assert opts.doc["subsection1"]["d"] is None
        assert opts.doc["subsection2"]["c"] == "option 2c"
        assert opts.subsection2.doc["c"] == "option 2c"
        assert opts.doc["subsection2"]["e"] is None
        assert opts.subsection2.subsubsection.doc["f"] == "option f"
        assert opts.subsection3.doc["z"] == "option z"


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
                check_all=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                check_any=[is_positive, lambda x: x < -20],
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
                check_all=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                check_any=[is_positive, lambda x: x < -20],
            ),
        )

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
        assert factory.create_immutable({"h": -21}).h == -21
        with pytest.raises(TypeError):
            opts = factory.create_immutable({"h": 3.5})
        with pytest.raises(ValueError):
            opts = factory.create_immutable({"a": -7})
        assert factory.create_immutable({"a": -23}).h == -21
        with pytest.raises(TypeError):
            opts = factory.create_immutable({"a": 3.5})

    def test_initialise_from_options(self):
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
                check_all=[is_positive, lambda x: x < 20],
            ),
            h=WithMeta(
                lambda options: options.a + 2,
                doc="option h",
                value_type=int,
                check_any=[is_positive, lambda x: x < -20],
            ),
        )

        opts1 = factory.create_immutable({"a": 4, "b": 5, "f": 3.0, "g": 13, "z": 17})

        opts2 = factory.create_immutable(opts1)

        assert dict(opts1) == dict(opts2)

        opts3 = factory.create(opts1)

        assert dict(opts1) == dict(opts3)

    def test_nested_from_parent(self):
        factory = MutableOptionsFactory(
            a=1,
            subsection=MutableOptionsFactory(
                b=2, c=lambda options: options.b + options.parent.a
            ),
        )

        opts = factory.create_immutable({})

        assert opts.a == 1
        assert opts.subsection.b == 2
        assert opts.subsection.c == 3

        opts2 = factory.create_immutable({"a": 4})

        assert opts2.a == 4
        assert opts2.subsection.b == 2
        assert opts2.subsection.c == 6

    def test_values_nested(self):
        factory = MutableOptionsFactory(a=1, subsection=MutableOptionsFactory(b=2), c=3)
        opts = factory.create_immutable({})
        values_iter = opts.values()
        assert next(values_iter) == 1
        value = next(values_iter)
        assert isinstance(value, MutableOptionsFactory.Options)
        assert dict(value) == {"b": 2}
        assert next(values_iter) == 3

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

    def test_add_defaults(self):
        subfactory = MutableOptionsFactory(
            d=WithMeta(4, doc="option d1"),
            e=WithMeta(5, doc="option e1"),
            f=WithMeta(6, doc="option f1"),
        )
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a1"),
            b=WithMeta(2, doc="option b1"),
            c=WithMeta(3, doc="option c1"),
            subsection=subfactory,
        )

        factory2 = factory.add(
            b=12,
            c=WithMeta(13, doc="option c2"),
            g=17,
            subsection={"d": 14, "e": WithMeta(15, doc="option e2"), "h": 18},
            subsection2=MutableOptionsFactory(i=WithMeta(19, doc="option i2")),
        )

        opts = factory2.create_immutable({})

        assert opts.a == 1
        assert opts.b == 12
        assert opts.c == 13
        assert opts.subsection.d == 14
        assert opts.subsection.e == 15
        assert opts.subsection.f == 6
        assert opts.g == 17
        assert opts.subsection.h == 18
        assert opts.subsection2.i == 19

        assert opts.doc["a"] == "option a1"
        assert opts.doc["b"] == "option b1"
        assert opts.doc["c"] == "option c2"
        assert opts.doc["subsection"]["d"] == "option d1"
        assert opts.doc["subsection"]["e"] == "option e2"
        assert opts.doc["subsection"]["f"] == "option f1"
        assert opts.doc["g"] is None
        assert opts.doc["subsection"]["h"] is None
        assert opts.doc["subsection2"]["i"] == "option i2"

        with pytest.raises(ValueError, match="Passing an OptionsFactory"):
            factory.add(a=MutableOptionsFactory(j=2))

        with pytest.raises(ValueError, match="Updating the section"):
            factory.add(subsection=MutableOptionsFactory(d=14, e=15, f=16))

    def test_add_initialise(self):
        subfactory = MutableOptionsFactory(
            d=WithMeta(4, doc="option d1"),
            e=WithMeta(5, doc="option e1"),
            f=WithMeta(6, doc="option f1"),
        )
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a1"),
            b=WithMeta(2, doc="option b1"),
            c=WithMeta(3, doc="option c1"),
            subsection=subfactory,
        )

        factory2 = factory.add(
            b=12,
            c=WithMeta(13, doc="option c2"),
            g=17,
            subsection={"d": 14, "e": WithMeta(15, doc="option e2"), "h": 18},
            subsection2=MutableOptionsFactory(i=WithMeta(19, doc="option i2")),
        )

        opts = factory2.create_immutable(
            {
                "a": 21,
                "b": 22,
                "c": 23,
                "subsection": {"d": 24, "e": 25, "f": 26, "h": 27},
                "g": 28,
                "subsection2": {"i": 29},
            }
        )

        assert opts.a == 21
        assert opts.b == 22
        assert opts.c == 23
        assert opts.subsection.d == 24
        assert opts.subsection.e == 25
        assert opts.subsection.f == 26
        assert opts.g == 28
        assert opts.subsection.h == 27
        assert opts.subsection2.i == 29

        assert opts.doc["a"] == "option a1"
        assert opts.doc["b"] == "option b1"
        assert opts.doc["c"] == "option c2"
        assert opts.doc["subsection"]["d"] == "option d1"
        assert opts.doc["subsection"]["e"] == "option e2"
        assert opts.doc["subsection"]["f"] == "option f1"
        assert opts.doc["g"] is None
        assert opts.doc["subsection"]["h"] is None
        assert opts.doc["subsection2"]["i"] == "option i2"

        with pytest.raises(ValueError, match="Passing an OptionsFactory"):
            factory.add(a=MutableOptionsFactory(j=2))

        with pytest.raises(ValueError, match="Updating the section"):
            factory.add(subsection=MutableOptionsFactory(d=14, e=15, f=16))

    def test_as_table(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create_immutable({"b": 3})
        assert opts.as_table() == as_table_test_str

    def test_as_table_nested(self):
        factory = MutableOptionsFactory(
            a=1,
            b=2,
            subsection1=MutableOptionsFactory(
                c=4, subsubsection=MutableOptionsFactory(d=5)
            ),
            subsection2=MutableOptionsFactory(e=6),
        )
        opts = factory.create_immutable({"b": 3})
        assert opts.as_table() == as_table_test_str_nested

    def test_str(self):
        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create_immutable({"b": 3})
        assert str(opts) == "{a: 1 (default), b: 3}"

    def test_str_nested(self):
        factory = MutableOptionsFactory(
            a=1,
            subsection=MutableOptionsFactory(
                c=3, subsubsection=MutableOptionsFactory(d=4)
            ),
            b=2,
        )
        opts = factory.create_immutable(
            {"b": 5, "subsection": {"subsubsection": {"d": 6}}}
        )
        assert (
            str(opts)
            == "{a: 1 (default), subsection: {c: 3 (default), subsubsection: {d: 6}}, "
            "b: 5}"
        )

    def test_create_from_yaml(self, tmp_path):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(a=1, b=2)

        with StringIO() as f:
            f.write("a: 3\nc: 4")

            # reset to beginning of f
            f.seek(0)

            opts = factory.create_immutable_from_yaml(f)

        assert opts.a == 3
        assert opts.b == 2

        with pytest.raises(TypeError):
            opts.a = 5

    def test_create_from_yaml_nested(self):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(
            a=1,
            b=2,
            subsection=MutableOptionsFactory(
                c=3, subsubsection=MutableOptionsFactory(d=4)
            ),
            e=5,
        )

        with StringIO() as f:
            f.write(
                "a: 11\ne: 15\nsubsection:\n  c: 13\n  subsubsection:\n    d: 14\nb: 12"
            )

            # reset to beginning of f
            f.seek(0)

            opts = factory.create_immutable_from_yaml(f)

        assert opts.a == 11
        assert opts.b == 12
        assert opts.subsection.c == 13
        assert opts.subsection.subsubsection.d == 14
        assert opts.e == 15

        with pytest.raises(TypeError):
            opts.a = 5

    def test_to_yaml(self):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(a=1, b=2)
        opts = factory.create_immutable({"a": 3})

        # file_like=None argument makes yaml.dump() return the YAML as a string
        assert opts.to_yaml(None) == "a: 3\n"
        assert opts.to_yaml(None, True) == "a: 3\nb: 2\n"

    def test_to_yaml_nested(self):
        pytest.importorskip("yaml")

        factory = MutableOptionsFactory(
            a=1,
            b=2,
            subsection=MutableOptionsFactory(
                c=3, subsubsection=MutableOptionsFactory(d=4)
            ),
            e=5,
        )

        opts = factory.create_immutable(
            {"a": 11, "subsection": {"c": 13, "subsubsection": {"d": 14}}}
        )

        assert (
            opts.to_yaml(None)
            == "a: 11\nsubsection:\n  c: 13\n  subsubsection:\n    d: 14\n"
        )

        assert (
            opts.to_yaml(None, True)
            == "a: 11\nb: 2\ne: 5\nsubsection:\n  c: 13\n  subsubsection:\n    d: 14\n"
        )

    def test_nested_defaults(self):
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a"),
            b=lambda options: options.subsection1.c
            + options.subsection2.subsubsection.f,
            subsection1=MutableOptionsFactory(c=WithMeta(3, doc="option 1c"), d=4),
            subsection2=MutableOptionsFactory(
                c=WithMeta(5, doc="option 2c"),
                e=6,
                subsubsection=MutableOptionsFactory(f=WithMeta(7, doc="option f")),
            ),
        )

        opts = factory.create_immutable({})

        assert opts.a == 1
        assert opts.b == 10
        assert opts.subsection1.c == 3
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 7

        assert opts.doc["a"] == "option a"
        assert opts.doc["b"] is None
        assert opts.doc["subsection1"]["c"] == "option 1c"
        assert opts.subsection1.doc["c"] == "option 1c"
        assert opts.doc["subsection1"]["d"] is None
        assert opts.doc["subsection2"]["c"] == "option 2c"
        assert opts.subsection2.doc["c"] == "option 2c"
        assert opts.doc["subsection2"]["e"] is None
        assert opts.subsection2.subsubsection.doc["f"] == "option f"

    def test_nested_initialise(self):
        factory = MutableOptionsFactory(
            a=WithMeta(1, doc="option a"),
            b=lambda options: options.subsection1.c
            + options.subsection2.subsubsection.f,
            subsection1=MutableOptionsFactory(c=WithMeta(3, doc="option 1c"), d=4),
            subsection2=MutableOptionsFactory(
                c=WithMeta(5, doc="option 2c"),
                e=6,
                subsubsection=MutableOptionsFactory(f=WithMeta(7, doc="option f")),
            ),
        )

        opts = factory.create_immutable(
            {
                "a": 2,
                "subsection1": {"c": 7},
                "subsection2": {"subsubsection": {"f": 8}},
            }
        )

        assert opts.a == 2
        assert opts.b == 15
        assert opts.subsection1.c == 7
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 8

        assert opts.doc["a"] == "option a"
        assert opts.doc["b"] is None
        assert opts.doc["subsection1"]["c"] == "option 1c"
        assert opts.subsection1.doc["c"] == "option 1c"
        assert opts.doc["subsection1"]["d"] is None
        assert opts.doc["subsection2"]["c"] == "option 2c"
        assert opts.subsection2.doc["c"] == "option 2c"
        assert opts.doc["subsection2"]["e"] is None
        assert opts.subsection2.subsubsection.doc["f"] == "option f"

        with pytest.raises(TypeError):
            opts.a = 3
        with pytest.raises(TypeError):
            opts.subsection1.d = 3
        with pytest.raises(TypeError):
            opts.subsection2.e = 3
        with pytest.raises(TypeError):
            opts.subsection2.subsubsection.f = 3

    def test_nested_with_arg_initialise(self):
        factory2 = MutableOptionsFactory(
            x=WithMeta(11, doc="option x"),
            y=12,
            subsection3=MutableOptionsFactory(z=WithMeta(13, doc="option z")),
        )

        factory = MutableOptionsFactory(
            factory2,
            a=WithMeta(1, doc="option a"),
            b=lambda options: options.subsection1.c
            + options.subsection2.subsubsection.f
            + options.subsection3.z,
            subsection1=MutableOptionsFactory(c=WithMeta(3, doc="option 1c"), d=4),
            subsection2=MutableOptionsFactory(
                c=WithMeta(5, doc="option 2c"),
                e=6,
                subsubsection=MutableOptionsFactory(f=WithMeta(7, doc="option f")),
            ),
        )

        opts = factory.create_immutable(
            {
                "a": 2,
                "x": 21,
                "subsection1": {"c": 7},
                "subsection2": {"subsubsection": {"f": 8}},
                "subsection3": {"z": 23},
            }
        )

        assert opts.a == 2
        assert opts.b == 38
        assert opts.x == 21
        assert opts.subsection1.c == 7
        assert opts.subsection1.d == 4
        assert opts.subsection2.c == 5
        assert opts.subsection2.e == 6
        assert opts.subsection2.subsubsection.f == 8
        assert opts.subsection3.z == 23

        assert opts.doc["a"] == "option a"
        assert opts.doc["b"] is None
        assert opts.doc["x"] == "option x"
        assert opts.doc["subsection1"]["c"] == "option 1c"
        assert opts.subsection1.doc["c"] == "option 1c"
        assert opts.doc["subsection1"]["d"] is None
        assert opts.doc["subsection2"]["c"] == "option 2c"
        assert opts.subsection2.doc["c"] == "option 2c"
        assert opts.doc["subsection2"]["e"] is None
        assert opts.subsection2.subsubsection.doc["f"] == "option f"
        assert opts.subsection3.doc["z"] == "option z"

        with pytest.raises(TypeError):
            opts.a = 3
        with pytest.raises(TypeError):
            opts.subsection1.d = 3
        with pytest.raises(TypeError):
            opts.subsection2.e = 3
        with pytest.raises(TypeError):
            opts.subsection2.subsubsection.f = 3
        with pytest.raises(TypeError):
            opts.subsection3.z = 3
