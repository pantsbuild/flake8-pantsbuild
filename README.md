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

| Error code | Description                                                  |
|:----------:|:------------------------------------------------------------:|
| PB800      | Found bad reference to class attribute                       |
| PB804      | Using a constant on the left-hand side of a logical operator |
| PB805      | Using a constant on the right-hand side of an and operator   |

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
