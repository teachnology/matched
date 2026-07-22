# matched
Python package for matching students to projects

## Development setup

This project uses [pre-commit](https://pre-commit.com) to run linting, formatting, and
basic hygiene checks automatically before each commit. To set it up locally (using
`uvx`, so nothing needs to be installed into your environment):

```bash
uvx pre-commit install
```

This registers the hooks defined in `.pre-commit-config.yaml` as a git hook, so they run
automatically on `git commit` from then on. To run them manually against all files at any
time (e.g. after first setting up):

```bash
uvx pre-commit run --all-files
```
