# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import print_function, unicode_literals, division, absolute_import

from textwrap import dedent

from flake8_pantsbuild import PB800


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
    assert PB800.format(name="Example", attr="CONSTANT") in result.out
    assert "./good.py" not in result.out
    assert "./bad.py:8:29" in result.out
