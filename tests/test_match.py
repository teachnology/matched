import pathlib

import pandas as pd

from matched import match, shortlist

CWD = pathlib.Path(__file__).parent
choices = pd.read_csv(CWD / "data" / "choices1.csv", comment="#")
nmax = pd.read_csv(CWD / "data" / "nmax1.csv", index_col=0, comment="#").iloc[:, 0]


class TestMatch:
    def test_match(self):
        allocations = match(choices, nmax)

        # No project has more students than nmax.
        assert nmax.sub(allocations.groupby("code").size(), fill_value=0).ge(0).all()

        # First choices.
        assert allocations.loc["mz6952", "code"] == "code1"
        assert allocations.loc["yzq85", "code"] == "code2"
        assert allocations.loc["gc48", "code"] == "code2"
        assert allocations.loc["jq1239", "code"] == "code3"

        assert allocations.loc["mz6952", "choice"] == 1
        assert allocations.loc["yzq85", "choice"] == 1
        assert allocations.loc["gc48", "choice"] == 1
        assert allocations.loc["jq1239", "choice"] == 1

        # Second choices.
        assert allocations.loc["xeq483", "choice"] == 2


class TestShortlist:
    def test_shortlist(self):
        shortlisted = shortlist(choices, "code1")
        assert shortlisted.code.eq("code1").all()
        assert len(shortlisted) == 4
        assert shortlisted.username.iloc[0] == "yzq85"
        assert shortlisted.username.iloc[-1] == "jq1239"
