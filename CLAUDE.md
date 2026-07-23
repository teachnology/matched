# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`matched` is a small Python package that matches students to projects based on
ranked preferences, project capacity, and student scores (e.g. for final-year
project allocation). It ships as a library (`src/matched`), not an application.

## Commands

This project uses `uv` for dependency management and packaging.

```bash
# Install dependencies (including dev group)
uv sync

# Run the full test suite (also runs doctests on the package and produces
# coverage output — configured via [tool.pytest.ini_options] in pyproject.toml)
uv run pytest

# Run a single test file / test
uv run pytest tests/test_match.py
uv run pytest tests/test_match.py::TestMatch::test_match

# Lint
uv run ruff check .

# Regenerate the synthetic test fixtures in tests/data/ (choices.csv, nmax.csv)
# using fakeitmakeit; only creates files that don't already exist
uv run python tests/data/_make.py
```

Notes on the test setup:
- `pytest` is configured (in `pyproject.toml`) with `--doctest-modules`, so
  docstring examples in `src/matched/*.py` are executed as part of the suite —
  keep any doctests in the source accurate.
- `pytest-xdist` runs tests in parallel (`-n auto`).
- Coverage excludes `tests/*.py` and is reported to terminal + `htmlcov/`.

## Code architecture

The package has two small, focused modules with a clear pipeline relationship:

- **`preprocess.py`** — cleans/filters a raw `choices` DataFrame before matching:
  - `filter_invalid_code` — drop rows whose project `code` isn't in the known project list.
  - `filter_invalid_course` — drop rows where the project isn't offered to the student's `course` (uses a `projects` DataFrame indexed by `code` with one boolean column per course).
  - `deduplicate` — collapse repeated `(username, code)` picks, keeping the lowest (best) `choice` rank.

  These are designed to be composed with `.pipe(...)`, in the order
  code-validity → course-validity → dedup (see `tests/test_preprocess.py`'s
  `TestCombined` for the canonical pipeline).

- **`match.py`** — the allocation algorithm, operating on the *cleaned* `choices` DataFrame:
  - `match(choices, nmax)` — round-robin allocation by choice rank. Each round
    processes the current best remaining choice for every unallocated student;
    within a project, students are ranked by `score` (descending) and admitted
    until `nmax` (a `pd.Series` indexed by project `code`) is reached, at which
    point that project is removed from consideration for the rest of the
    round. Returns a DataFrame indexed by `username` with `code`/`choice`
    columns; unallocated students get `NaN` in both.
  - `shortlist(choices, code)` — students who picked a given project, sorted
    by score descending (independent of `match`, used for manual/human review
    of a project's applicant pool).

### Data contracts (DataFrame shapes used throughout)

- `choices`: one row per student preference, columns `username`, `code`,
  `choice` (1 = first preference), `score`; optionally `course` (required
  only for `filter_invalid_course`).
- `projects`: indexed by `code`, with an `nmax` column (capacity) and one
  boolean column per course name (used only by `filter_invalid_course`).
- `nmax` (as passed to `match`): a `pd.Series` indexed by project `code` —
  typically `projects.nmax`.

`tests/data/choices.csv` and `tests/data/projects.csv` are the canonical
fixtures illustrating these shapes (including `#`-commented rows documenting
*why* each row is invalid/duplicate — read these comments when adding cases).

## Docstring style

Numpy-style docstrings (`convention = "numpy"` under `[tool.ruff.lint.pydocstyle]`),
enforced by ruff's `D` rules. Every public function needs `Parameters`,
`Returns`, and (if applicable) `Raises` sections — see `match.py`/`preprocess.py`
for the expected format.

## Documentation

- Built with MkDocs Material + `mkdocstrings` (API reference) + `mkdocs-jupyter`
  (tutorial notebooks), config in `mkdocs.yml`. Deps live in the `docs`
  dependency group (`uv sync --group docs`); build with
  `uv run mkdocs build --strict`, preview with `uv run mkdocs serve`.
- `docs/notebooks/` holds the getting-started tutorial notebooks (`01-data`,
  `02-preprocessing`, `03-algorithm` — data shape, preprocessing, then the
  allocation algorithm itself), each executed fresh at doc-build time (ruff
  also lints notebooks via `extend-include = ["*.ipynb"]`).
  `docs/notebooks/raw/` holds the real-shaped anonymized input CSVs they use.
  Notebook outputs are stripped on commit by `nbstripout` — only the code
  needs to be correct, not committed outputs.
- `docs/index.md` (home) and `docs/reference.md` (API reference) are the
  other two docs pages.
- Deployed to GitHub Pages via `.github/workflows/docs.yml`: builds (and, on
  `main`, deploys) on every push/PR using `actions/upload-pages-artifact` +
  `actions/deploy-pages` — requires the repo's Pages source to be set to
  "GitHub Actions" (Settings → Pages).

## Other

- Requires Python >= 3.13 (`.python-version` pins the dev interpreter to 3.14).
