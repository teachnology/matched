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

See the [documentation](https://teachnology.github.io/matched/) for a full
getting-started tutorial and the API reference.

## Contributing

Issues and pull requests are welcome.

## Citation

If you use `matched` in your work, please cite it as described in
[CITATION.cff](CITATION.cff).

## License

MIT — see [LICENSE](LICENSE).
