# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

# NB: Flit uses this as our distribution description.
"""Various Flake8 lints used by the Pants projects and its users."""

from __future__ import absolute_import, division, print_function, unicode_literals

import ast
import sys

# NB: Flit uses this as our distribution version.
PY2 = sys.version_info[0] < 3
__version__ = "0.1.0" if not PY2 else b"0.1.0"


PB800 = (
    "PB800 Instead of {name}.{attr} use self.{attr} or cls.{attr} with instance methods and "
    "classmethods, respectively."
)


class Visitor(ast.NodeVisitor):
    """Various lints used by the Pants project and its users."""

    def __init__(self):
        self.errors = []

    def visit_ClassDef(self, class_node):
        for node in ast.walk(class_node):
            is_class_attribute = isinstance(node, ast.Attribute) and isinstance(
                node.value, ast.Name
            )
            if is_class_attribute and node.value.id == class_node.name:
                self.errors.append(
                    (
                        node.value.lineno,
                        node.value.col_offset,
                        PB800.format(name=class_node.name, attr=node.attr),
                    )
                )


class Plugin(object):
    name = "flake8-pantsbuild"
    version = __version__

    def __init__(self, tree):
        self._tree = tree

    def run(self):
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
