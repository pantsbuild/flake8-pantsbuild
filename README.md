# flake8-pantsbuild

This Flake8 plugin provides several custom lints used by the Pants project and its users.

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

## Usage

If using with Pants, run `./pants lint file.py` as usual.

If using without Pants, run `flake8 file.py` [as usual](http://flake8.pycqa.org/en/latest/user/invocation.html).

## Error Codes

| Error code | Description                                                     | Notes                |
|:----------:|:---------------------------------------------------------------:|:--------------------:|
| PB100      | Check for 2-space indentation                                   | Disabled by default¹ |
| PB200      | Check for trailing whitespace                                   | Disabled by default² |
| PB201      | Check for trailing slashes (`\`)                                | Disabled by default² |
| PB601      | Using old style `except` statements instead of the `as` keyword | Disabled by default³ |
| PB602      | Using `iteritems`, `iterkeys`, or `itervalues`                  | Disabled by default³ |
| PB603      | Using `xrange`                                                  | Disabled by default³ |
| PB604      | Using `basestring` or `unicode`                                 | Disabled by default³ |
| PB605      | Using metaclasses incompatible with Python 3                    | Disabled by default³ |
| PB606      | Found Python 2 old-style classes (not inheriting `object`)      | Disabled by default³ |
| PB607      | Using print statements, rather than print functions             | Disabled by default³ |
| PB800      | Used class attribute that breaks inheritance                    |                      |
| PB802      | Using `open` without a `with` statement (context manager)       |                      |
| PB804      | Using a constant on the left-hand side of a logical operator    |                      |
| PB805      | Using a constant on the right-hand side of an and operator      |                      |

¹ To enable the `PB100` indentation lint, set `--enable-extensions=PB100`. You'll need to disable `E111` (check for 4-space indentation) via `--extend-ignore=E111`. You'll likely want to disable `E121`, `E124`, `E125`, `E127`, and `E128` as well.
² To enable the `PB2*` trailing whitespace lints, set `--enable-extensions=PB2`. You'll need to disable `W291` and `W293`, which are stricter versions of the `PB2*` lints, via `--extend-ignore=W291,W293`.
³ To enable the `PB6*` checks for Python 2->3 lints, set `--enable-extensions=PB6`. 

## Migration from `pantsbuild.pants.contrib.python.checks.checker`

TODO

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
