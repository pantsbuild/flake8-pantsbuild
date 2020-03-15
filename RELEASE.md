# Release Process

You must first have [`Poetry`](https://python-poetry.org/docs/) installed.

## Preparation

### Version Bump and Changelog

Create a pull request to prepare the release:

1. Bump the `version` in `pyproject.toml`.
1. Update `CHANGELOG.md`.
    1. Run `git log --oneline v1.0.0..HEAD` for the commit titles, where `v.1.0.0` is the tag for the prior release.
    1. Link to the actual PR for each commit. See the prior release notes for an example.

Once green and reviewed, merge to master.

### Tag the commit

Pull master to get the release prep commit locally. Then, tag the commit:

1. `git tag --sign -a v1.1.0 HEAD`
1. `git push --tags origin HEAD`

## PyPI Release

See https://python-poetry.org/docs/libraries/#publishing-to-pypi.

```bash
$ poetry --build publish
```
