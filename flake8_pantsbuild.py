# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, division, print_function, unicode_literals

import ast
import re
import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

PY2 = sys.version_info[0] < 3

PB601 = (
    "PB601 Using an old-style except statement. Instead of `except ValueError, e`, use "
    "`except ValueError as e`."
)
PB605 = (
    "PB605 Using the old style of declaring metaclasses, which won't work properly with Python 3. "
    "If you need to support both Python 2 and Python 3, use either `with_metaclass` or "
    "`add_metaclass` from `six` or `future`. If you don't care about Python 2 support, use "
    "`class Example(metaclass=MyMetaclass)`."
)
PB606 = "PB606 Classes must be new-style classes, meaning they inherit `object` or another class."
PB607 = (
    "PB607 Print used as a statement. Please either use `from __future__ import print_function` or "
    "rewrite to look like a function call, e.g. change `print 'hello'` to `print('hello')`."
)
PB800 = (
    "PB800 Instead of {name}.{attr} use self.{attr} or cls.{attr} with instance methods and "
    "classmethods, respectively."
)
PB802 = "PB802 `open()` calls should be made within a `with` statement (context manager)"
PB804 = "PB804 Using a constant on the left-hand side of a logical operator."
PB805 = "PB805 Using a constant on the right-hand side of an `and` operator."


class Visitor(ast.NodeVisitor):
    """Various lints used by the Pants project and its users."""

    PRINT_FUNCTION_REGEX = re.compile(r"^\s*\(.*\)\s*$")

    def __init__(self, lines):
        self.lines = lines
        self.errors = []
        self.with_call_exprs = set()

    def collect_call_exprs_from_with_node(self, with_node):
        """Save any functions within a `with` statement to `self.with_call_exprs`.

        This is needed for checking PB802.
        """
        if PY2:
            expr = with_node.context_expr
            with_context_exprs = {expr} if isinstance(expr, ast.Call) else set()
        else:
            with_context_exprs = {
                node.context_expr
                for node in with_node.items
                if isinstance(node.context_expr, ast.Call)
            }
        self.with_call_exprs.update(with_context_exprs)

    def check_for_pb601(self, try_except_node):
        for handler in try_except_node.handlers:
            logical_line = self.lines[handler.lineno - 1]
            except_offset = logical_line.index("except")
            stripped_line = logical_line[except_offset + len("except") :]
            if handler.name and " as " not in stripped_line:
                self.errors.append((handler.lineno, handler.col_offset, PB601))

    def check_for_pb605(self, class_def_node):
        for node in class_def_node.body:
            if not isinstance(node, ast.Assign):
                continue
            for name in node.targets:
                if not isinstance(name, ast.Name):
                    continue
                if name.id == "__metaclass__":
                    self.errors.append((name.lineno, name.col_offset, PB605))

    def check_for_pb606(self, class_def_node):
        if not class_def_node.bases:
            self.errors.append((class_def_node.lineno, class_def_node.col_offset, PB606))

    def check_for_pb607(self, print_node):
        # This checks for a print statement being used _like_ a print function, e.g.
        # `print("hello")`. It is still technically a print _statement_ rather than _function_, but
        # it behaves the same as a print function.
        logical_line = self.lines[print_node.lineno - 1]
        print_offset = logical_line.index("print")
        stripped_line = logical_line[print_offset + len("print") :]
        if not self.PRINT_FUNCTION_REGEX.match(stripped_line):
            self.errors.append((print_node.lineno, print_node.col_offset, PB607))

    def check_for_pb800(self, class_def_node):
        for node in ast.walk(class_def_node):
            is_class_attribute = isinstance(node, ast.Attribute) and isinstance(
                node.value, ast.Name
            )
            if is_class_attribute and node.value.id == class_def_node.name:
                self.errors.append(
                    (
                        node.value.lineno,
                        node.value.col_offset,
                        PB800.format(name=class_def_node.name, attr=node.attr),
                    )
                )

    def check_for_pb802(self, call_node):
        if (
            isinstance(call_node.func, ast.Name)
            and call_node.func.id == "open"
            and call_node not in self.with_call_exprs
        ):
            self.errors.append((call_node.lineno, call_node.col_offset, PB802))

    def check_for_pb804_and_pb805(self, bool_op_node):
        def is_constant(expr):
            if PY2:
                is_name_constant = isinstance(expr, ast.Name) and expr.id in (
                    "True",
                    "False",
                    "None",
                )
            else:
                is_name_constant = isinstance(expr, ast.NameConstant)
            return isinstance(expr, (ast.Num, ast.Str)) or is_name_constant

        if not isinstance(bool_op_node.op, (ast.And, ast.Or)):
            return
        leftmost = bool_op_node.values[0]
        rightmost = bool_op_node.values[-1]
        if is_constant(leftmost):
            self.errors.append((leftmost.lineno, leftmost.col_offset, PB804))
        if isinstance(bool_op_node.op, ast.And) and is_constant(rightmost):
            self.errors.append((rightmost.lineno, rightmost.col_offset, PB805))

    def visit_BoolOp(self, bool_op_node):
        self.check_for_pb804_and_pb805(bool_op_node)

    def visit_Call(self, call_node):
        self.check_for_pb802(call_node)

    def visit_ClassDef(self, class_def_node):
        self.check_for_pb605(class_def_node)
        self.check_for_pb606(class_def_node)
        self.check_for_pb800(class_def_node)

    def visit_Print(self, print_node):
        # NB: When running with Python 3, this method will never be called because Print does not
        # exist in the AST. This will also not be called when using
        # `from __future__ import print_function` with Python 2.
        self.check_for_pb607(print_node)

    def visit_TryExcept(self, try_except_node):
        # NB: This method will not be called with Python 3 because TryExcept and TryFinally were
        # merged into Try.
        self.check_for_pb601(try_except_node)

    def visit_With(self, with_node):
        self.collect_call_exprs_from_with_node(with_node)


class Plugin(object):
    name = "flake8-pantsbuild"
    version = version("flake8-pantsbuild")

    def __init__(self, tree, lines):
        self._tree = tree
        self._lines = lines

    def run(self):
        visitor = Visitor(lines=self._lines)
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
