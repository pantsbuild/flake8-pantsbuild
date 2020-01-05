# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import ast
from textwrap import dedent

from flake8_pantsbuild import Plugin


def results(s):
    return {"{}:{}: {}".format(*r) for r in Plugin(ast.parse(s)).run()}


def test_pnt_800():
    template = dedent(
        """\
        import os.path
      
      
        class Example(object):
            CONSTANT = "foo"
      
            def foo(self, value):
                return os.path.join({}.CONSTANT, value)
        """
    )
    good = template.format("self")
    bad = template.format("Example")
    assert results(good) == set()
    assert results(bad) == {
        "8:29: PNT800 Instead of Example.CONSTANT use self.CONSTANT or cls.CONSTANT with "
        "instance methods and classmethods, respectively."
    }
