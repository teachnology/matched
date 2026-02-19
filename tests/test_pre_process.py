import pathlib

import pandas as pd
import pytest

from matched import deduplicate

CWD = pathlib.Path(__file__).parent


@pytest.fixture
def choices_duplicated():
    return pd.read_csv(CWD / "data" / "choices_duplicated.csv")


def test_deduplicate(choices_duplicated):
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
