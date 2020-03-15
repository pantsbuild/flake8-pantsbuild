# flake8-pantsbuild

This Flake8 plugin provides several custom lints used by the Pants project and its users.

## Table of Contents

* [Installation](#installation)
    * [Supported Python versions](#supported-python-versions)
* [Usage](#usage)
* [Error Codes](#error-codes)
* [Migrating from `lint.pythonstyle` to `flake8`](#migrating-from-lintpythonstyle-to-flake8)
    * [Differences between the tools](#differences-between-the-tools)
    * [Steps to migrate](#steps-to-migrate)
    * [Alternatives to custom lints](#alternatives-to-custom-lints)
* [Development](#development)

## Installation

If using with Pants, add this to your `pants.toml`:

```toml
[GLOBAL]
backend_packages2.add = ["pants.backend.python.lint.flake8"]

[flake8]
extra_requirements.add = ["flake8-pantsbuild"]
```

If using Flake8 without Pants, install with:

```bash
$ pip install flake8-pantsbuild
```

### Supported Python versions

This plugin works with Python 2.7 and 3.5+.

## Usage

If using with Pants, run `./pants lint file.py` as usual.

If using without Pants, run `flake8 file.py` [as usual](http://flake8.pycqa.org/en/latest/user/invocation.html).

## Error Codes

| Error code | Description                                                     | Notes                |
|:----------:|:---------------------------------------------------------------:|:--------------------:|
| PB10       | Using class attribute that breaks inheritance                   |                      |
| PB11       | Using a constant on the left-hand side of a logical operator    |                      |
| PB12       | Using a constant on the right-hand side of an and operator      |                      |
| PB13       | Using `open` without a `with` statement (context manager)       |                      |
| PB20       | Check for 2-space indentation                                   | Disabled by default¹ |
| PB30       | Using slashes instead of parentheses for line continuation      | Disabled by default² |
| PB60       | Using `print` statements, rather than the `print` function      | Disabled by default³ |
| PB61       | Using old style `except` statements instead of the `as` keyword | Disabled by default³ |
| PB62       | Using `iteritems`, `iterkeys`, or `itervalues`                  | Disabled by default³ |
| PB63       | Using `xrange`                                                  | Disabled by default³ |
| PB64       | Using `basestring` or `unicode`                                 | Disabled by default³ |
| PB65       | Using metaclasses incompatible with Python 3                    | Disabled by default³ |
| PB66       | Using Python 2 old-style classes (not inheriting `object`)      | Disabled by default³ |

¹ To enable the `PB20` indentation lint, set `--enable-extensions=PB20`. You'll need to disable `E111` (check for 4-space indentation) via `--extend-ignore=E111`. You'll likely want to disable `E121`, `E124`, `E125`, `E127`, and `E128` as well.

² To enable the `PB30` trailing slash lint, set `--enable-extensions=PB30`.

³ To enable the `PB6*` checks for Python 2->3 lints, set `--enable-extensions=PB6`. 

## Migrating from `lint.pythonstyle` to `flake8`

`lint.pythonstyle` was a custom Pants task from the `pants.contrib.python.checks` plugin that behaved like Flake8, but was generally inferior to the more popular Flake8.

### Differences between the tools 

Pants' `lint.pythonstyle` task runs `pycodestyle` and `pyflakes`, in addition to providing several custom lints. 

In contrast, Flake8 runs `pycodestyle` and `pyflakes`, but it also uses `mccabe` to check for complex sections of code and it [adds its own lints](https://flake8.pycqa.org/en/latest/user/error-codes.html). Flake8 does not have any of the custom `lint.pythonstyle` lints by default, but the [below table](#alternatives-to-custom-lints) shows how to keep any of these lints you'd like.

Flake8 has hundreds of plugins that you may easily add to Pants. See [Awesome Flake8 Extensions](https://github.com/DmytroLitvinov/awesome-flake8-extensions) for a curated list of plugins.

### Steps to migrate

First, follow the [installation instructions](#installation) to hook up Flake8 with Pants. Then, disable `lint.pythonstyle` by removing `pants.contrib.python.checks` from your `pants.toml`.

Then, run Flake8 by running `./pants lint file.py` (see [Usage](#usage)).

The first time you run `./pants lint` , you will likely have several errors due to its differences with `lint.pythonstyle`. We recommend starting by [disabling](https://flake8.pycqa.org/en/latest/user/violations.html) those errors in a [`.flake8` config file](https://flake8.pycqa.org/en/latest/user/configuration.html). Add this to your `pants.toml` to ensure Pants uses the config:

```toml
[flake8]
config = "path/to/.flake8"
```

If you want to keep any of the custom lints from `lint.pythonstyle`, refer to the below table. You will need to install additional plugins by adding this to your `pants.toml`:

```toml
[flake8]
extra_requirements.add = [
  "flake8-pantsbuild",
  "pep8-naming",
  "flake8-import-order",
  # and so on...
]
```

### Alternatives to custom lints

| Old code | Old option scope            | Description                                                     | Alternative                               |
|:--------:|:---------------------------:|:---------------------------------------------------------------:|:-----------------------------------------:|
| T000     | pycheck-variable-names      | Class names must be `UpperCamelCase`                            | `pep8-naming` Flake8 plugin               |
| T001     | pycheck-variable-names      | Class globals must be `UPPER_SNAKE_CASED`                       | `pep8-naming` Flake8 plugin               |
| T002     | pycheck-variable-names      | Function names must be `lower_snake_cased`                      | `pep8-naming` Flake8 plugin               |
| T100     | pycheck-indentation         | Enforce 2-space indentation                                     | `PB20`¹                                   |
| T200     | pycheck-trailing-whitespace | Trailing whitespace                                             | Flake8's `W291`                           |
| T201     | pycheck-trailing-whitespace | Using slashes instead of parentheses for line continuation      | `PB30`¹                                   |
| T301     | pycheck-newlines            | Excepted 1 blank line between class methods                     | Flake8's `E301` and `E303`                |
| T302     | pycheck-newlines            | Excepted 2 blank lines between top level definitions            | Flake8's `E302` and `E303`                |
| T400     | pycheck-import-order        | Wildcard imports not allowed                                    | `isort` or `flake8-import-order` plugin ² |
| T401     | pycheck-import-order        | `from` imports not sorted correctly                             | `isort` or `flake8-import-order` plugin ² |
| T402     | pycheck-import-order        | `import` should only import one module at a time                | `isort` or `flake8-import-order` plugin ² |
| T403     | pycheck-import-order        | Importing multiple module types in one statement                | `isort` or `flake8-import-order` plugin ² |
| T404     | pycheck-import-order        | Unclassifiable import                                           | `isort` or `flake8-import-order` plugin ² |
| T405     | pycheck-import-order        | Import block has multiple module types                          | `isort` or `flake8-import-order` plugin ² |
| T406     | pycheck-import-orde         | Out of order import statements                                  | `isort` or `flake8-import-order` plugin ² |
| T601     | pycheck-except-statement    | Using old style `except` statements instead of the `as` keyword | `PB61`¹                                   |
| T602     | pycheck-future-compat       | Using `iteritems`, `iterkeys`, or `itervalues`                  | `PB62`¹                                   |
| T603     | pycheck-future-compat       | Using `xrange`                                                  | `PB63`¹                                   |
| T604     | pycheck-future-compat       | Using `basestring` or `unicode`                                 | `PB64`¹                                   |
| T605     | pycheck-future-compat       | Using metaclasses incompatible with Python 3                    | `PB65`¹                                   |
| T606     | pycheck-new-style-classes   | Found Python 2 old-style classes (not inheriting `object`)      | `PB66`¹                                   |
| T607     | pycheck-print-statements    | Using `print` statements, rather than the `print` function      | `PB60`¹                                   |
| T800     | pycheck-class-factoring     | Using class attribute that breaks inheritance                   | `PB10`                                    |
| T801     | pycheck-variable-names      | Shadowing a `builtin` name                                      | `flake8-builtins` plugin                  |
| T802     | pycheck-context-manager     | Using `open` without a `with` statement (context manager)       | `PB13`                                    |
| T803     | pycheck-except-statement    | Using a blanket `except:`                                       | Flake8's `E722`                           |
| T804     | pycheck-constant-logic      | Using a constant on the left-hand side of a logical operator    | `PB11`                                    |
| T805     | pycheck-constant-logic      | Using a constant on the right-hand side of an and operator      | `PB12`                                    |

¹ This lint is disabled by default. See the above section [`Error Codes`](#error-codes) for instructions on how to enable this lint.

² To use `isort` with Pants, set `backend_packages2.add = ["pants.backend.python.lint.isort"]` in your `pants.toml`.

## Development

We use [tox](https://testrun.org/tox/en/latest/) for test automation. To run the test suite, invoke tox:

```bash
$ tox
```

You may run certain environments with `tox -e` (run `tox -a` to see all options):

```bash
$ tox -e format-run
$ tox -e py27
$ tox -e py36
```

You may also manually test by building a [PEX](https://github.com/pantsbuild/pex) with this plugin, as follows:

```bash
$ pex flake8 . --entry-point flake8 --output-file flake8.pex
$ vim example.py  # add whatever content you want
$ ./flake.pex example.py
```
