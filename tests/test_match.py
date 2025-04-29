import pathlib

import pandas as pd

from matched import match

CWD = pathlib.Path(__file__).parent
choices = pd.read_csv(CWD / "data" / "choices.csv")
nmax = pd.read_csv(CWD / "data" / "nmax.csv", index_col=0).iloc[:, 0]


def test_match():
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
