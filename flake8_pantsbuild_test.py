# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, division, print_function, unicode_literals

from textwrap import dedent

from flake8_pantsbuild import PB800

# NB: `pytest-flake8dir` has a known issue that it runs our plugin twice for every test. This means
# tha result.out will have the same error twice for every file. This is a known issue and was fixed
# in 2.1.0, but we can't upgrade past 1.3.0 due to needing to support Python 2. So, we convert
# result.out_lines to a set in every test for deduplication.
# See https://pypi.org/project/pytest-flake8dir/.


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
