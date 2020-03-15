# -*- coding: utf-8 -*-
# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import absolute_import, division, print_function, unicode_literals

import ast
import re
import sys
import tokenize
from collections import defaultdict

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

PLUGIN_NAME = "flake8_pantsbuild"
PLUGIN_VERSION = version(PLUGIN_NAME)

PY2 = sys.version_info[0] < 3

PB10 = (
    "PB10 Instead of {name}.{attr} use self.{attr} or cls.{attr} with instance methods and "
    "classmethods, respectively, so that inheritance works correctly."
)
PB11 = (
    "PB11 Using a constant on the left-hand side of a logical operator. This means that the "
    "left-hand side will always be truthy, so condition will short-circuit and the right-hand side "
    "will never be evaluated."
)
PB12 = (
    "PB12 Using a constant on the right-hand side of an `and` operator. This means that the "
    "right-hand side will always be truthy, which is likely not expected."
)
PB13 = (
    "PB13 `open()` calls should be made within a `with` statement (context manager). This is "
    "important to ensure that the file handler is properly cleaned up."
)

PB20 = "PB20 Indentation of {} instead of 2."

PB30 = (
    "PB30 Using a trailing slash (`\\`) instead of parentheses for line continuation. Refer "
    "to https://www.tutorialspoint.com/How-to-wrap-long-lines-in-Python."
)

PB61 = (
    "PB61 Using an old-style except statement. Instead of `except ValueError, e`, use "
    "`except ValueError as e`."
)
PB62 = (
    "PB62 `{bad_attr}()` is removed in Python 3. Instead, use `{good_attr}()` or use "
    "`six.{bad_attr}()`."
)
PB63 = "PB63 `xrange()` is removed in Python 3. Instead, use `range()` or use `six.range()`."
PB64 = "PB64 {bad_name} is removed in Python 3. Instead, use `six.{six_replacement}`."
PB65 = (
    "PB65 Using the old style of declaring metaclasses, which won't work properly with Python 3. "
    "If you need to support both Python 2 and Python 3, use either `with_metaclass` or "
    "`add_metaclass` from `six` or `future`. If you don't care about Python 2 support, use "
    "`class Example(metaclass=MyMetaclass)`."
)
PB66 = "PB66 Classes must be new-style classes, meaning they inherit `object` or another class."
PB60 = (
    "PB60 Print used as a statement. Please either use `from __future__ import print_function` or "
    "rewrite to look like a function call, e.g. change `print 'hello'` to `print('hello')`."
)


class Visitor(ast.NodeVisitor):
    """Various lints used by the Pants project and its users."""

    def __init__(self):
        self.errors = []
        self.with_call_exprs = set()

    def collect_call_exprs_from_with_node(self, with_node):
        """Save any functions within a `with` statement to `self.with_call_exprs`.

        This is needed for checking PB13.
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

    def check_for_pb10(self, class_def_node):
        for node in ast.walk(class_def_node):
            is_class_attribute = isinstance(node, ast.Attribute) and isinstance(
                node.value, ast.Name
            )
            if is_class_attribute and node.value.id == class_def_node.name:
                self.errors.append(
                    (
                        node.value.lineno,
                        node.value.col_offset,
                        PB10.format(name=class_def_node.name, attr=node.attr),
                    )
                )

    def check_for_pb11_and_pb12(self, bool_op_node):
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
            self.errors.append((leftmost.lineno, leftmost.col_offset, PB11))
        if isinstance(bool_op_node.op, ast.And) and is_constant(rightmost):
            self.errors.append((rightmost.lineno, rightmost.col_offset, PB12))

    def check_for_pb13(self, call_node):
        if (
            isinstance(call_node.func, ast.Name)
            and call_node.func.id == "open"
            and call_node not in self.with_call_exprs
        ):
            self.errors.append((call_node.lineno, call_node.col_offset, PB13))

    def visit_BoolOp(self, bool_op_node):
        self.check_for_pb11_and_pb12(bool_op_node)
        self.generic_visit(bool_op_node)

    def visit_Call(self, call_node):
        self.check_for_pb13(call_node)
        self.generic_visit(call_node)

    def visit_ClassDef(self, class_def_node):
        self.check_for_pb10(class_def_node)
        self.generic_visit(class_def_node)

    def visit_With(self, with_node):
        self.collect_call_exprs_from_with_node(with_node)
        self.generic_visit(with_node)


class Plugin(object):
    name = PLUGIN_NAME
    version = PLUGIN_VERSION

    def __init__(self, tree):
        self._tree = tree

    def run(self):
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)


class OptionalPlugin(object):
    """A plugin that's disabled by default."""

    name = PLUGIN_NAME
    version = PLUGIN_VERSION
    off_by_default = True
    codes = []

    @classmethod
    def is_enabled(cls, options):
        return any(code in options.enable_extensions for code in cls.codes)


class IndentationPlugin(OptionalPlugin):
    """Lint for 2-space indentation.

    This is disabled by default because it conflicts with Flake8's default settings of 4-space
    indentation.
    """

    codes = ["PB2", "PB20"]

    def __init__(self, tree, file_tokens, options):
        self._tokens = file_tokens
        self._options = options
        self.errors = []

    def run(self):
        if not self.is_enabled(self._options):
            return
        self.check_for_pb20(self._tokens)
        for line, col, msg in self.errors:
            yield line, col, msg, type(self)

    def check_for_pb20(self, tokens):
        indents = []
        for token in tokens:
            token_type, token_text, token_start = token[0:3]
            if token_type is tokenize.DEDENT:
                indents.pop()
            if token_type is tokenize.INDENT:
                last_indent = len(indents[-1]) if indents else 0
                current_indent = len(token_text)
                indents.append(token_text)
                if current_indent - last_indent != 2:
                    lineno, col_offset = token_start
                    self.errors.append(
                        (lineno, col_offset, PB20.format(current_indent - last_indent))
                    )


class TrailingSlashesPlugin(OptionalPlugin):
    """Check for trailing slashes.

    Flake8 does not automatically check for trailing slashes, but this is a subjective style
    preference so should be disabled by default.
    """

    codes = ["PB3", "PB30"]

    def __init__(self, tree, lines, file_tokens, options):
        self._lines = lines
        self._tokens = file_tokens
        self._options = options
        self.errors = []

    def run(self):
        if not self.is_enabled(self._options):
            return
        self.check_for_pb30(self._lines, self._tokens)
        for line, col, msg in self.errors:
            yield line, col, msg, type(self)

    def check_for_pb30(self, lines, tokens):
        lines = [line.rstrip("\n") for line in lines]
        # First generate a set of ranges where we accept trailing slashes, specifically within
        # comments and strings
        exception_map = defaultdict(list)
        for token in tokens:
            token_type, _, token_start, token_end = token[0:4]
            if token_type not in (tokenize.COMMENT, tokenize.STRING):
                continue
            token_start_line, token_start_col_offset = token_start
            token_end_line, token_end_col_offset = token_end
            if token_start_line == token_end_line:
                exception_map[token_start_line].append(
                    (token_start_col_offset, token_end_col_offset)
                )
            else:
                exception_map[token_start_line].append((token_start_col_offset, sys.maxsize))
                for line in range(token_start_line + 1, token_end_line):
                    exception_map[line].append((0, sys.maxsize))
                exception_map[token_end_line].append((0, token_end_col_offset))

        def has_exception(lineno, col_offset):
            for start, end in exception_map.get(lineno, []):
                if start <= col_offset <= end:
                    return True
            return False

        for line_number, line in enumerate(lines):
            # Tokens are 1-indexed, rather than 0-indexed.
            line_number += 1
            stripped_line = line.rstrip()
            col_offset = len(stripped_line) - 1
            if stripped_line.endswith("\\") and not has_exception(line_number, col_offset):
                self.errors.append((line_number, col_offset, PB30))


class SixVisitor(ast.NodeVisitor):

    PRINT_FUNCTION_REGEX = re.compile(r"^\s*\(.*\)\s*$")

    def __init__(self, lines):
        self.lines = lines
        self.errors = []

    def check_for_pb60(self, print_node):
        # This checks for a print statement being used _like_ a print function, e.g.
        # `print("hello")`. It is still technically a print _statement_ rather than _function_, but
        # it behaves the same as a print function.
        logical_line = self.lines[print_node.lineno - 1]
        print_offset = logical_line.index("print")
        stripped_line = logical_line[print_offset + len("print") :]
        if not self.PRINT_FUNCTION_REGEX.match(stripped_line):
            self.errors.append((print_node.lineno, print_node.col_offset, PB60))

    def check_for_pb61(self, try_except_node):
        for handler in try_except_node.handlers:
            logical_line = self.lines[handler.lineno - 1]
            except_offset = logical_line.index("except")
            stripped_line = logical_line[except_offset + len("except") :]
            if handler.name and " as " not in stripped_line:
                self.errors.append((handler.lineno, handler.col_offset, PB61))

    def check_for_pb62_and_63(self, call_node):
        dict_iterators = {"iteritems": "items", "iterkeys": "keys", "itervalues": "values"}
        if isinstance(call_node.func, ast.Attribute):
            # Not a perfect solution since a user could have a dictionary named six or something
            # similar. However, this should catch most cases where people are using iter* without
            # six.
            attr = call_node.func.attr
            if attr in dict_iterators and getattr(call_node.func.value, "id") != "six":
                self.errors.append(
                    (
                        call_node.lineno,
                        call_node.col_offset,
                        PB62.format(bad_attr=attr, good_attr=dict_iterators[attr]),
                    )
                )
        if isinstance(call_node.func, ast.Name) and call_node.func.id == "xrange":
            self.errors.append((call_node.lineno, call_node.col_offset, PB63))

    def check_for_pb64(self, name_node):
        bad_names = {"basestring": "string_types", "unicode": "text_type"}
        name = name_node.id
        if name in bad_names:
            self.errors.append(
                (
                    name_node.lineno,
                    name_node.col_offset,
                    PB64.format(bad_name=name, six_replacement=bad_names[name]),
                )
            )

    def check_for_pb65(self, class_def_node):
        for node in class_def_node.body:
            if not isinstance(node, ast.Assign):
                continue
            for name in node.targets:
                if not isinstance(name, ast.Name):
                    continue
                if name.id == "__metaclass__":
                    self.errors.append((name.lineno, name.col_offset, PB65))

    def check_for_pb66(self, class_def_node):
        if not class_def_node.bases:
            self.errors.append((class_def_node.lineno, class_def_node.col_offset, PB66))

    def visit_Call(self, call_node):
        self.check_for_pb62_and_63(call_node)
        self.generic_visit(call_node)

    def visit_ClassDef(self, class_def_node):
        self.check_for_pb65(class_def_node)
        self.check_for_pb66(class_def_node)
        self.generic_visit(class_def_node)

    def visit_Name(self, name_node):
        self.check_for_pb64(name_node)
        self.generic_visit(name_node)

    def visit_Print(self, print_node):
        self.check_for_pb60(print_node)
        self.generic_visit(print_node)

    def visit_TryExcept(self, try_except_node):
        self.check_for_pb61(try_except_node)
        self.generic_visit(try_except_node)


class SixPlugin(OptionalPlugin):
    """Several lints to help with Python 2->3 migrations."""

    codes = ["PB6"]

    def __init__(self, tree, lines, options):
        self._tree = tree
        self._lines = lines
        self._options = options

    def run(self):
        if not self.is_enabled(self._options):
            return
        visitor = SixVisitor(lines=self._lines)
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)
