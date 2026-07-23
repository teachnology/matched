# matched

[![tests](https://github.com/teachnology/matched/actions/workflows/tests.yml/badge.svg)](https://github.com/teachnology/matched/actions/workflows/tests.yml)
[![ruff](https://github.com/teachnology/matched/actions/workflows/ruff.yml/badge.svg)](https://github.com/teachnology/matched/actions/workflows/ruff.yml)
[![PyPI](https://img.shields.io/pypi/v/matched)](https://pypi.org/project/matched/)
[![License](https://img.shields.io/pypi/l/matched)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-teachnology.github.io%2Fmatched-blue)](https://teachnology.github.io/matched/)

Python package for matching students to projects based on ranked preferences,
project capacity, and student scores (e.g. for final-year project
allocation).

## Installation

```bash
uv add matched
```

or

```bash
pip install matched
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

See the [documentation](https://teachnology.github.io/matched/) for a full
getting-started tutorial and the API reference.

## Contributing

Issues and pull requests are welcome.

## Citation

If you use `matched` in your work, please cite it as described in
[CITATION.cff](CITATION.cff).

## License

MIT — see [LICENSE](LICENSE).
