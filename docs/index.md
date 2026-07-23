# matched

`matched` is a small Python package for matching students to projects based on
ranked preferences, project capacity, and student scores — for example, for
final-year project allocation.

## Installation

```bash
uv add matched
```

## Quick example

```python
import matched

choices = {"alice": ["code1", "code2"], "bob": ["code1"]}
scores = {"alice": 90, "bob": 70}
courses = {"alice": "course1", "bob": "course2"}
nmax = {"code1": 1, "code2": 2}
eligible_courses = {"code1": ["course1", "course2"], "code2": ["course1"]}

choices = matched.filter_invalid_code(choices, nmax)
choices = matched.filter_invalid_course(choices, courses, eligible_courses)
choices = matched.deduplicate(choices)

allocation = matched.match(choices, scores, nmax)
```

See [Getting started](notebooks/01-data.ipynb) for a full worked example, or
the [API reference](reference.md) for details on individual functions.
