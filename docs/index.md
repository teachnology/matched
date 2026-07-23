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
import pandas as pd

import matched

choices = pd.read_csv("choices.csv")
projects = pd.read_csv("projects.csv", index_col="code")

choices = (
    choices.pipe(matched.filter_invalid_code, valid_codes=projects.index)
    .pipe(matched.filter_invalid_course, projects=projects)
    .pipe(matched.deduplicate)
)

allocation = matched.match(choices, nmax=projects.nmax)
```

See [Getting started](notebooks/01-data.ipynb) for a full worked example, or
the [API reference](reference.md) for details on individual functions.
