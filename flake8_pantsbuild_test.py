# Copyright 2020 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import itertools
from textwrap import dedent

from flake8_pantsbuild import PB10, PB11, PB12, PB13, PB20, PB30


def test_pb_10(flake8dir):
    template = dedent(
        """\
        import os.path


        class Example:
            CONSTANT = "foo"

            def foo(self, value):
                return os.path.join({}.CONSTANT, value)
        """
    )
    flake8dir.make_py_files(good=template.format("self"), bad=template.format("Example"))
    result = flake8dir.run_flake8()
    assert [f"./bad.py:8:29: {PB10.format(name='Example', attr='CONSTANT')}"] == result.out_lines


def test_pb_11(flake8dir):
    violating_pairs = itertools.product([None, False, True, 1, "'a'"], ["or", "and"])
    violations = {
        f"bad{i}": f"x = 0\n{pair[0]} {pair[1]} x" for i, pair in enumerate(violating_pairs)
    }
    flake8dir.make_py_files(good="x = y = 0\nx or y", **violations)
    result = flake8dir.run_flake8()
    assert sorted(f"./{fp}.py:2:1: {PB11}" for fp in violations) == sorted(result.out_lines)


def test_pb_12(flake8dir):
    violations = {
        f"bad{i}": f"x = 0\nx and {constant}"
        for i, constant in enumerate([None, False, True, 1, "'a'"])
    }
    flake8dir.make_py_files(good="x = y = 0\nx and y", **violations)
    result = flake8dir.run_flake8()
    assert sorted(f"./{fp}.py:2:7: {PB12}" for fp in violations) == sorted(result.out_lines)


def test_pb_13(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            foo = open('test.txt')

            with open('test.txt'):
                pass

            bar = open('test.txt')

            with open('test.txt') as fp:
                fp.read()
            """
        )
    )
    result = flake8dir.run_flake8()
    assert [f"./example.py:1:7: {PB13}", f"./example.py:6:7: {PB13}"] == result.out_lines


def test_pb_20(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            def one():
             pass


            def four():
                pass


            def two():
              pass


            def hanging():
              _ = (
                  "this"
                  "is"
                  "ok")
            """
        )
    )
    result = flake8dir.run_flake8(
        extra_args=["--enable-extensions", "PB20", "--extend-ignore", "E111"]
    )
    assert [
        f"./example.py:2:1: {PB20.format('1')}",
        f"./example.py:6:1: {PB20.format('4')}",
    ] == result.out_lines


def test_pb_30(flake8dir):
    flake8dir.make_example_py(
        dedent(
            """\
            from textwrap import dedent

            bad = \\
                123

            also_bad = "hello" \\
                "world"

            okay = '''
                str1 \\
                str2 \\
                str3
                '''

            also_okay = dedent(
                '''\
                str
                '''
            )

            # this is okay too \\
            """
        )
    )
    result = flake8dir.run_flake8(extra_args=["--enable-extensions", "PB30"])
    assert [f"./example.py:3:7: {PB30}", f"./example.py:6:20: {PB30}"] == result.out_lines
