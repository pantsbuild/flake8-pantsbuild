# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import ast
import sys
import tokenize
from collections import defaultdict
from typing import Iterator, List, NamedTuple, Set

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version

PLUGIN_NAME = "flake8_pantsbuild"
PLUGIN_VERSION = version(PLUGIN_NAME)

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


class Error(NamedTuple):
    lineno: int
    col_offset: int
    msg: str


class Visitor(ast.NodeVisitor):
    """Various lints used by the Pants project and its users."""

    def __init__(self) -> None:
        self.errors: List[Error] = []
        self.with_call_exprs: Set = set()

    def collect_call_exprs_from_with_node(self, with_node: ast.With) -> None:
        """Save any functions within a `with` statement to `self.with_call_exprs`.

        This is needed for checking PB13.
        """
        with_context_exprs = {
            node.context_expr for node in with_node.items if isinstance(node.context_expr, ast.Call)
        }
        self.with_call_exprs.update(with_context_exprs)

    def check_for_pb10(self, class_def_node: ast.ClassDef) -> None:
        for node in ast.walk(class_def_node):
            if not isinstance(node, ast.Attribute):
                continue
            attribute_value = node.value
            if isinstance(attribute_value, ast.Name) and attribute_value.id == class_def_node.name:
                self.errors.append(
                    Error(
                        attribute_value.lineno,
                        attribute_value.col_offset,
                        PB10.format(name=class_def_node.name, attr=node.attr),
                    )
                )

    def check_for_pb11_and_pb12(self, bool_op_node: ast.BoolOp) -> None:
        def is_constant(expr):
            return isinstance(expr, (ast.Num, ast.Str)) or isinstance(expr, ast.NameConstant)

        if not isinstance(bool_op_node.op, (ast.And, ast.Or)):
            return
        leftmost = bool_op_node.values[0]
        rightmost = bool_op_node.values[-1]
        if is_constant(leftmost):
            self.errors.append(Error(leftmost.lineno, leftmost.col_offset, PB11))
        if isinstance(bool_op_node.op, ast.And) and is_constant(rightmost):
            self.errors.append(Error(rightmost.lineno, rightmost.col_offset, PB12))

    def check_for_pb13(self, call_node: ast.Call) -> None:
        if (
            isinstance(call_node.func, ast.Name)
            and call_node.func.id == "open"
            and call_node not in self.with_call_exprs
        ):
            self.errors.append(Error(call_node.lineno, call_node.col_offset, PB13))

    def visit_BoolOp(self, bool_op_node: ast.BoolOp) -> None:
        self.check_for_pb11_and_pb12(bool_op_node)
        self.generic_visit(bool_op_node)

    def visit_Call(self, call_node: ast.Call) -> None:
        self.check_for_pb13(call_node)
        self.generic_visit(call_node)

    def visit_ClassDef(self, class_def_node: ast.ClassDef) -> None:
        self.check_for_pb10(class_def_node)
        self.generic_visit(class_def_node)

    def visit_With(self, with_node: ast.With) -> None:
        self.collect_call_exprs_from_with_node(with_node)
        self.generic_visit(with_node)


class Plugin:
    name = PLUGIN_NAME
    version = PLUGIN_VERSION

    def __init__(self, tree) -> None:
        self._tree = tree

    def run(self) -> Iterator:
        visitor = Visitor()
        visitor.visit(self._tree)
        for line, col, msg in visitor.errors:
            yield line, col, msg, type(self)


class OptionalPlugin:
    """A plugin that's disabled by default."""

    name = PLUGIN_NAME
    version = PLUGIN_VERSION
    off_by_default = True
    codes: List[str] = []

    @classmethod
    def is_enabled(cls, options) -> bool:
        return any(code in options.enable_extensions for code in cls.codes)


class IndentationPlugin(OptionalPlugin):
    """Lint for 2-space indentation.

    This is disabled by default because it conflicts with Flake8's default settings of 4-space
    indentation.
    """

    codes = ["PB2", "PB20"]

    def __init__(self, tree, file_tokens, options) -> None:
        self._tokens = file_tokens
        self._options = options
        self.errors: List[Error] = []

    def run(self) -> Iterator:
        if not self.is_enabled(self._options):
            return
        self.check_for_pb20(self._tokens)
        for line, col, msg in self.errors:
            yield line, col, msg, type(self)

    def check_for_pb20(self, tokens) -> None:
        indents: List[str] = []
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
                        Error(lineno, col_offset, PB20.format(current_indent - last_indent))
                    )


class TrailingSlashesPlugin(OptionalPlugin):
    """Check for trailing slashes.

    Flake8 does not automatically check for trailing slashes, but this is a subjective style
    preference so should be disabled by default.
    """

    codes = ["PB3", "PB30"]

    def __init__(self, tree, lines, file_tokens, options) -> None:
        self._lines = lines
        self._tokens = file_tokens
        self._options = options
        self.errors: List[Error] = []

    def run(self) -> Iterator:
        if not self.is_enabled(self._options):
            return
        self.check_for_pb30(self._lines, self._tokens)
        for line, col, msg in self.errors:
            yield line, col, msg, type(self)

    def check_for_pb30(self, lines, tokens) -> None:
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
                for lineno in range(token_start_line + 1, token_end_line):
                    exception_map[lineno].append((0, sys.maxsize))
                exception_map[token_end_line].append((0, token_end_col_offset))

        def has_exception(lineno: int, col_offset: int) -> bool:
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
                self.errors.append(Error(line_number, col_offset, PB30))
