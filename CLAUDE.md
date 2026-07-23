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
```

Notes on the test setup:
- `pytest` is configured (in `pyproject.toml`) with `--doctest-modules`, so
  docstring examples in `src/matched/*.py` are executed as part of the suite —
  keep any doctests in the source accurate.
- `pytest-xdist` runs tests in parallel (`-n auto`).
- Coverage excludes `tests/*.py` and is reported to terminal + `htmlcov/`.

## Code architecture

The package has two small, focused modules with a clear pipeline relationship.
The public API takes/returns plain Python `dict`/`list` values (no DataFrames,
no bespoke classes) — internally, functions are free to convert to
`pd.DataFrame`/`Series` for vectorized work where that's cleaner.

- **`preprocess.py`** — cleans/filters a raw `choices` dict before matching:
  - `filter_invalid_code(choices, nmax)` — drop codes not present in `nmax`
    (i.e. not a known project).
  - `filter_invalid_course(choices, courses, eligible_courses)` — drop codes
    not eligible for the student's course.
  - `deduplicate(choices)` — collapse repeated codes in a student's list,
    keeping the first (best/lowest rank) occurrence.

  These all take/return the `choices` dict shape, so they compose by
  sequential reassignment, in the order code-validity → course-validity →
  dedup (see `tests/test_preprocess.py`'s `TestCombined` for the canonical
  pipeline):

  ```python
  cleaned = filter_invalid_code(choices, nmax)
  cleaned = filter_invalid_course(cleaned, courses, eligible_courses)
  cleaned = deduplicate(cleaned)
  ```

- **`match.py`** — the allocation algorithm, operating on the *cleaned*
  `choices` dict:
  - `match(choices, scores, nmax)` — round-robin allocation by choice rank
    (rank implied by each student's list position). Each round processes the
    current best remaining choice for every unallocated student; within a
    project, students are ranked by `scores` (descending) and admitted until
    `nmax` is reached, at which point that project is removed from
    consideration for the rest of the round. Returns `{username: code}`
    (allocated project code); unallocated students map to `None`. Internally
    builds a "long" DataFrame (one row per (username, code)) to reuse
    pandas' vectorized groupby/sort operations for the round-robin loop.
  - `choice_rank(choices, allocated)` — given `match()`'s result, looks up
    each allocated student's choice rank (`choices[username].index(code) +
    1`), or `None` if unallocated. Decoupled from `match()` since not every
    caller needs the rank.
  - `shortlist(choices, scores, code)` — usernames who picked a given
    project, sorted by score descending (independent of `match`, used for
    manual/human review of a project's applicant pool).

### Data contracts (plain dict/list shapes used throughout)

- `choices`: `{username: [code, ...]}` — ordered list of project codes per
  student; rank is implied by position (index 0 = first choice).
- `scores`: `{username: score}`.
- `courses`: `{username: course}` — the student's course (only needed for
  `filter_invalid_course`).
- `nmax`: `{code: max_capacity}` — passed to `filter_invalid_code` and
  `match`.
- `eligible_courses`: `{code: [course, ...]}` — courses eligible for each
  project (only needed for `filter_invalid_course`).

`tests/test_preprocess.py` and `tests/test_match.py` define these as inline
dict literals in their fixtures — the canonical illustration of these
shapes (including inline comments documenting *why* each entry is
invalid/duplicate — read these when adding cases).

## Docstring style

Numpy-style docstrings (`convention = "numpy"` under `[tool.ruff.lint.pydocstyle]`),
enforced by ruff's `D` rules. Every public function needs `Parameters`,
`Returns`, and (if applicable) `Raises` sections — see `match.py`/`preprocess.py`
for the expected format. Every public function also has an `Examples` section with
a doctest (`import matched` + `matched.func(...)`, per the project's call-style
convention) — these run as part of the test suite via `--doctest-modules`, so a
failure there is a real regression, not flaky notebook output.

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
