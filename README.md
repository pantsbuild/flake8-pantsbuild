# flake8-pantsbuild

This Flake8 plugin provides several custom lints used by the Pants project and its users.

## Installation

If using with Pants, add this to your `pants.ini`:

```ini
[GLOBAL]
backend_packages2: +['pants.backend.python.lint.flake8']

[flake8]
extra_requirements: +['flake8-pantsbuild']
```

If using Flake8 without Pants, install with:

```bash
$ pip install flake8-pantsbuild
```

## Usage

If using with Pants, run `./pants lint2 ::` as usual.

If using without Pants, run `flake8 your_module.py` [as usual](http://flake8.pycqa.org/en/latest/user/invocation.html).

## Error Codes

| Error code | Description                            |
|:----------:|:--------------------------------------:|
| PNT800     | Found bad reference to class attribute |

## Migration from `pantsbuild.pants.contrib.python.checks.checker`

TODO

## Developers Guide

We use [Poetry](https://python-poetry.org) for dependency management, building the wheel, and publishing.

### To install

```bash
$ poetry install
```

This will use whichever version `python` points to. You can set `poetry env use python3.7`, for example, to point to a different Python discoverable on your PATH.

### To test

```bash
$ poetry run pytest
```

You may also manually test by building a PEX with this plugin, as follows:

```bash
$ poetry build
$ pex flake8 dist/flake8_pantsbuild-0.1.0-py2.py3-none-any.whl --entry-point flake8 --interpreter-constraint='CPython>=3.6' --output-file flake8.pex
$ vim example.py  # add whatever content you want
$ ./flake.pex example.py
```

### To publish

```bash
$ poetry build
$ poetry publish
```
