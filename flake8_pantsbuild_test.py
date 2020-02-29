# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, division, print_function, unicode_literals

import itertools
from textwrap import dedent

from flake8_pantsbuild import PB800, PB802, PB804, PB805

# NB: `pytest-flake8dir` has a known issue that it runs our plugin twice for every test. This means
# that result.out will have the same error twice for every file. This was fixed in 2.1.0, but we
# can't upgrade past 1.3.0 due to needing to support Python 2. So, we convert result.out_lines to
# a set in every test for deduplication. See https://pypi.org/project/pytest-flake8dir/.


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
    good = dedent(
        """\
        with open('test.txt'):
            pass

        with open('test.txt') as fp:
            fp.read()
        """
    )
    bad = dedent(
        """\
        foo = open('test.txt')

        with open('test.txt'):
            pass

        bar = open('test.txt')
        """
    )
    flake8dir.make_py_files(good=good, bad=bad)
    result = flake8dir.run_flake8()
    assert {"./bad.py:1:7: {}".format(PB802), "./bad.py:6:7: {}".format(PB802)} == set(
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
