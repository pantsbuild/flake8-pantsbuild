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
| PB10       | Used class attribute that breaks inheritance                    |                      |
| PB11       | Using a constant on the left-hand side of a logical operator    |                      |
| PB12       | Using a constant on the right-hand side of an and operator      |                      |
| PB13       | Using `open` without a `with` statement (context manager)       |                      |
| PB20       | Check for 2-space indentation                                   | Disabled by default¹ |
| PB30       | Using slashes instead of parentheses for line continuation      | Disabled by default² |
| PB60       | Using print statements, rather than print functions             | Disabled by default³ |
| PB61       | Using old style `except` statements instead of the `as` keyword | Disabled by default³ |
| PB62       | Using `iteritems`, `iterkeys`, or `itervalues`                  | Disabled by default³ |
| PB63       | Using `xrange`                                                  | Disabled by default³ |
| PB64       | Using `basestring` or `unicode`                                 | Disabled by default³ |
| PB65       | Using metaclasses incompatible with Python 3                    | Disabled by default³ |
| PB66       | Found Python 2 old-style classes (not inheriting `object`)      | Disabled by default³ |

¹ To enable the `PB20` indentation lint, set `--enable-extensions=PB20`. You'll need to disable `E111` (check for 4-space indentation) via `--extend-ignore=E111`. You'll likely want to disable `E121`, `E124`, `E125`, `E127`, and `E128` as well.
² To enable the `PB30` trailing slash lint, set `--enable-extensions=PB30`.
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
