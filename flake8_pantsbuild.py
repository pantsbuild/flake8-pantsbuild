# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

"""Various Flake8 lints used by the Pants projects and its users."""  # NB: Flit uses this as out distribution description.

import ast


__version__ = "0.1.0"  # NB: Flit uses this as out distribution version.

PB800 = (
    "PB800 Instead of {name}.{attr} use self.{attr} or cls.{attr} with instance methods and "
    "classmethods, respectively."
)


class Visitor(ast.NodeVisitor):
    """Various lints used by the Pants project and its users."""

    def __init__(self):
        self.errors = []  # type: List[Tuple[int, int, str]]

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
