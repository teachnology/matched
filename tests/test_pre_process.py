import pathlib

import pandas as pd
import pytest

from matched import deduplicate, filter_invalid_course

CWD = pathlib.Path(__file__).parent


@pytest.fixture
def choices_duplicated():
    return pd.read_csv(CWD / "data" / "choices_duplicated.csv", comment="#")


@pytest.fixture
def choices_valid():
    return pd.read_csv(CWD / "data" / "choices1.csv", comment="#")


@pytest.fixture
def nmax():
    return pd.read_csv(CWD / "data" / "nmax1.csv", index_col="code", comment="#")


class TestDeduplicate:
    def test_deduplicate(self, choices_duplicated):
        deduped = deduplicate(choices_duplicated)

        # No (username, code) pair is duplicated.
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

    def test_deduplicate_nothing_to_do(self, choices_valid):
        assert deduplicate(choices_valid).equals(choices_valid)


class TestFilterInvalidCourse:
    def test_filter_invalid_course(self, choices_valid, nmax):
        filtered = filter_invalid_course(choices_valid, nmax)
        assert len(choices_valid) - len(filtered) == 4
