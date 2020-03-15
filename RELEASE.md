# Release Process

## Prerequisites

* Install [`Poetry`](https://python-poetry.org/docs/).
* Set up PGP and PyPI. See https://www.pantsbuild.org/release.html#0-prerequisites.

## Preparation

### Version Bump and Changelog

Create a pull request to prepare the release:

1. Bump the `version` in `pyproject.toml`.
1. Update `CHANGELOG.md`.
    1. Run `git log --oneline 1.0.0..HEAD` for the commit titles, where `1.0.0` is the tag for the prior release.
    1. Link to the actual PR for each commit. See the prior release notes for an example.

Include the PR title and link for the release prep PR you are creating in the CHANGELOG, even though it has not yet landed in master.

Once green and reviewed, merge to master.

### Tag the commit

Pull master to get the release prep commit locally. Then, tag the commit:

1. `git tag --sign -a 1.1.0 -m "Release 1.1.0" HEAD`
1. `git push --tags origin HEAD`

## PyPI Release

See https://python-poetry.org/docs/libraries/#publishing-to-pypi.

```bash
$ poetry publish --build
```
