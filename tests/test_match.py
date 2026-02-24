import pathlib

import pandas as pd
import numpy as np
import pytest

from matched import (
    deduplicate,
    filter_invalid_code,
    filter_invalid_course,
    match,
    shortlist,
)

CWD = pathlib.Path(__file__).parent


@pytest.fixture
def choices(projects):
    return (
        pd.read_csv(CWD / "data" / "choices.csv", comment="#")
        .pipe(filter_invalid_code, valid_codes=projects.index)
        .pipe(filter_invalid_course, projects=projects)
        .pipe(deduplicate)
    )


@pytest.fixture
def projects():
    return pd.read_csv(CWD / "data" / "projects.csv", index_col="code", comment="#")


class TestMatch:
    def test_match(self, choices, projects):
        allocations = match(choices, projects.nmax)

        # No project has more students than nmax.
        assert (
            projects.nmax.sub(allocations.groupby("code").size(), fill_value=0)
            .ge(0)
            .all()
        )

        assert allocations.loc["mz6952", "code"] == "code1"
        assert allocations.loc["gc48", "code"] == "code2"
        assert allocations.loc["jq1239", "code"] == "code3"
        assert allocations.loc["yzq85", "code"] == "code3"

        assert allocations.loc["mz6952", "choice"] == 1
        assert allocations.loc["gc48", "choice"] == 1
        assert allocations.loc["jq1239", "choice"] == 1
        assert allocations.loc["yzq85", "choice"] == 2

        # Unsuccessfully allocated student has NaN for both 'code' and 'choice'.
        assert np.isnan(allocations.loc["xeq483", "code"])
        assert np.isnan(allocations.loc["xeq483", "choice"])


class TestShortlist:
    def test_shortlist(self, choices):
        shortlisted = shortlist(choices, "code1")
        assert shortlisted.code.eq("code1").all()
        assert len(shortlisted) == 4
        assert shortlisted.iloc[0].name == "yzq85"
        assert shortlisted.iloc[-1].name == "jq1239"
