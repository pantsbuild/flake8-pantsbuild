# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, division, print_function, unicode_literals

import itertools
from textwrap import dedent

import pytest

from flake8_pantsbuild import (
    PB100,
    PB201,
    PB601,
    PB602,
    PB603,
    PB604,
    PB605,
    PB606,
    PB607,
    PB800,
    PB802,
    PB804,
    PB805,
    PY2,
)

# NB: `pytest-flake8dir` has a known issue that it runs our plugin twice for every test. This means
# that result.out will have the same error twice for every file. This was fixed in 2.1.0, but we
# can't upgrade past 1.3.0 due to needing to support Python 2. So, we convert result.out_lines to
# a set in every test for deduplication. See https://pypi.org/project/pytest-flake8dir/.


def test_pb_100(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            def one():
             pass


            def four():
                pass


            def two():
              pass


            def hanging():
              _ = (
                  "this"
                  "is"
                  "ok")
            """
        )
    )
    result = flake8dir.run_flake8(
        extra_args=["--enable-extensions", "PB100", "--extend-ignore", "E111"]
    )
    assert {
        "./example.py:2:1: {}".format(PB100.format("1")),
        "./example.py:6:1: {}".format(PB100.format("4")),
    } == set(result.out_lines)


def test_pb_201(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            from textwrap import dedent

            bad = \\
                123

            also_bad = "hello" \\
                "world"

            okay = '''
                str1 \\
                str2 \\
                str3
                '''

            also_okay = dedent(
                '''\
                str
                '''
            )

            # this is okay too \\
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB201"])
    assert {"./example.py:3:7: {}".format(PB201), "./example.py:6:20: {}".format(PB201)} == set(
        result.out_lines
    )


@pytest.mark.skipif(not PY2, reason="Old-style exceptions cause syntax error with Python 3")
def test_pb_601(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            try:
                pass
            except ValueError, e:
                raise e

            try:
                pass
            except (ValueError, TypeError), e:
                raise e

            try:
                pass
            except ValueError:
                raise

            try:
                pass
            except ValueError as e:
                raise e

            try:
                pass
            except (ValueError, TypeError) as e:
                raise e
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB6"])
    assert {"./example.py:3:1: {}".format(PB601), "./example.py:8:1: {}".format(PB601)} == set(
        result.out_lines
    )


def test_pb_602(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            import six
            from six import iteritems

            d1 = {"hello": 0}

            # Bad
            d1.iteritems()
            d1.iterkeys()
            d1.itervalues()

            # Good
            d1.items()
            d1.keys()
            d1.values()
            six.iteritems()
            iteritems(d1)

            # We don't actually check that it's a dictionary. We only
            # check for the method name.
            o = object()
            o.iteritems()
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB6"])
    assert {
        "./example.py:7:1: {}".format(PB602.format(bad_attr="iteritems", good_attr="items")),
        "./example.py:8:1: {}".format(PB602.format(bad_attr="iterkeys", good_attr="keys")),
        "./example.py:9:1: {}".format(PB602.format(bad_attr="itervalues", good_attr="values")),
        "./example.py:21:1: {}".format(PB602.format(bad_attr="iteritems", good_attr="items")),
    } == set(result.out_lines)


@pytest.mark.skipif(not PY2, reason="`xrange()` does not exist in Python 3`")
def test_pb_603(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            import six

            # Bad
            xrange(10)

            # Good
            range(10)
            six.range()
            o = object()
            o.xrange()
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB6"])
    assert {"./example.py:4:1: {}".format(PB603)} == set(result.out_lines)


@pytest.mark.skipif(not PY2, reason="`basestring` and `unicode` do not exist in Python 3`")
def test_pb_604(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            assert isinstance("txt", unicode)
            assert isinstance("txt", basestring)
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB6"])
    assert {
        "./example.py:1:26: {}".format(
            PB604.format(bad_name="unicode", six_replacement="text_type")
        ),
        "./example.py:2:26: {}".format(
            PB604.format(bad_name="basestring", six_replacement="string_types")
        ),
    } == set(result.out_lines)


def test_pb_605(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            from fake import SingletonMetaclass
            from six import add_metaclass, with_metaclass


            class Singleton(object):
                __metaclass__ = SingletonMetaclass


            @add_metaclass(SingletonMetaclass)
            class SafeSingleton(object):
                pass


            class SafeSingleton2(with_metaclass(object, SingletonMetaclass)):
                pass
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB6"])
    assert {"./example.py:6:5: {}".format(PB605)} == set(result.out_lines)


def test_pb_606(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            from fake import Super1, Super2


            class OldStyle:
                pass


            class NewStyle(object):
                pass


            class Subclass(Super1, Super2):
                pass


            class NoMroSpecified():
                pass
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB6"])
    assert {"./example.py:4:1: {}".format(PB606), "./example.py:16:1: {}".format(PB606)} == set(
        result.out_lines
    )


@pytest.mark.skipif(not PY2, reason="Print statements cause syntax errors with Python 3")
def test_pb_607(flake8dir):
    flake8dir.make_py_files(
        normal=dedent(
            """\
            # Good
            print("I'm a statement, but look like a function call")
            print(0, 1, 2)
            print (0, 1, 2)

            # Bad
            print "old school"
            print 0
            """
        ),
        future=dedent(
            """\
            from __future__ import print_function

            print("Future-proof!")
            """
        ),
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB6"])
    assert {"./normal.py:7:1: {}".format(PB607), "./normal.py:8:1: {}".format(PB607)} == set(
        result.out_lines
    )


def test_pb_800(flake8dir):
    template = dedent(
        """\
        import os.path


        class Example(object):
            CONSTANT = "foo"

            def foo(self, value):
                return os.path.join({}.CONSTANT, value)
        """
    )
    flake8dir.make_py_files(good=template.format("self"), bad=template.format("Example"))
    result = flake8dir.run_flake8()
    assert {"./bad.py:8:29: {}".format(PB800.format(name="Example", attr="CONSTANT"))} == set(
        result.out_lines
    )


def test_pb_802(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            foo = open('test.txt')

            with open('test.txt'):
                pass

            bar = open('test.txt')

            with open('test.txt') as fp:
                fp.read()
            """
        )
    )
    result = flake8dir.run_flake8()
    assert {"./example.py:1:7: {}".format(PB802), "./example.py:6:7: {}".format(PB802)} == set(
        result.out_lines
    )


def test_pb_804(flake8dir):
    violating_pairs = itertools.product([None, False, True, 1, "'a'"], ["or", "and"])
    violations = {
        "bad{}".format(i): "x = 0\n{constant} {op} x".format(constant=pair[0], op=pair[1])
        for i, pair in enumerate(violating_pairs)
    }
    flake8dir.make_py_files(good="x = y = 0\nx or y", **violations)
    result = flake8dir.run_flake8()
    assert {"./{}.py:2:1: {}".format(fp, PB804) for fp in violations} == set(result.out_lines)


def test_pb_805(flake8dir):
    violations = {
        "bad{}".format(i): "x = 0\nx and {}".format(constant)
        for i, constant in enumerate([None, False, True, 1, "'a'"])
    }
    flake8dir.make_py_files(good="x = y = 0\nx and y", **violations)
    result = flake8dir.run_flake8()
    assert {"./{}.py:2:7: {}".format(fp, PB805) for fp in violations} == set(result.out_lines)
