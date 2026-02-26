import pathlib

import pandas as pd
import pytest

from matched import deduplicate, filter_invalid_code, filter_invalid_course

CWD = pathlib.Path(__file__).parent


@pytest.fixture
def choices():
    return pd.read_csv(CWD / "data" / "choices.csv", comment="#")


@pytest.fixture
def projects():
    return pd.read_csv(CWD / "data" / "projects.csv", index_col="code", comment="#")


class TestDeduplicate:
    def test_deduplicate(self, choices):
        deduped = deduplicate(choices)

        # No "(username, code)" pair is duplicated.
        assert not deduped.duplicated(subset=["username", "code"]).any()

        # For each (username, code) pair, the row with the lowest choice number is kept.
        assert (
            deduped.loc[
                (deduped.username == "yzq85") & (deduped.code == "code1"), "choice"
            ].item()
            == 3
        )

        assert (
            deduped.loc[
                (deduped.username == "xeq483") & (deduped.code == "code3"), "choice"
            ].item()
            == 2
        )

        assert len(choices) - len(deduped) == 2


class TestFilterInvalidCode:
    def test_filter_invalid_code(self, choices, projects):
        filtered = filter_invalid_code(choices, projects.index)

        assert len(choices) - len(filtered) == 2


class TestFilterInvalidCourse:
    def test_filter_invalid_course(self, choices, projects):
        filtered = choices.pipe(filter_invalid_code, valid_codes=projects.index).pipe(
            filter_invalid_course, projects=projects
        )

        assert (
            len(choices) - len(filtered) == 6
        )  # 2 from invalid code + 4 from invalid course


class TestCombined:
    def test_combined(self, choices, projects):
        tweaked = (
            choices.pipe(filter_invalid_code, valid_codes=projects.index)
            .pipe(filter_invalid_course, projects=projects)
            .pipe(deduplicate)
        )

        assert len(choices) - len(tweaked) == 8
