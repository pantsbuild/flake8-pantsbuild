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
