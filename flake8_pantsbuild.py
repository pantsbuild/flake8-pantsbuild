# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, division, print_function, unicode_literals

import ast
import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

PY2 = sys.version_info[0] < 3

PB800 = (
    "PB800 Instead of {name}.{attr} use self.{attr} or cls.{attr} with instance methods and "
    "classmethods, respectively."
)
PB804 = "PB804 using a constant on the left-hand side of a logical operator."
PB805 = "PB805 using a constant on the right-hand side of an `and` operator."


class Visitor(ast.NodeVisitor):
    """Various lints used by the Pants project and its users."""

    def __init__(self):
        self.errors = []

    def visit_BoolOp(self, bool_op_node):
        def is_constant(expr):
            if PY2:
                is_name_constant = isinstance(expr, ast.Name) and expr.id in [
                    "True",
                    "False",
                    "None",
                ]
            else:
                is_name_constant = isinstance(expr, ast.NameConstant)
            return isinstance(expr, (ast.Num, ast.Str)) or is_name_constant

        if isinstance(bool_op_node.op, (ast.And, ast.Or)):
            leftmost = bool_op_node.values[0]
            rightmost = bool_op_node.values[-1]
            if is_constant(leftmost):
                self.errors.append((leftmost.lineno, leftmost.col_offset, PB804))
            if isinstance(bool_op_node.op, ast.And) and is_constant(rightmost):
                self.errors.append((rightmost.lineno, rightmost.col_offset, PB805))

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
    version = version("flake8-pantsbuild")

    def __init__(self, tree):
        self._tree = tree

    def run(self):
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
