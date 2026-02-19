import pandas as pd


def deduplicate(choices):
    """
    Deduplicate student project choices.

    For each (username, code) pair, only the row with the lowest choice number is kept.
    This handles the case where a student has selected the same project more than once
    across different preference ranks.

    Parameters
    ----------
    choices : pd.DataFrame
        DataFrame containing the students' choices. It must have the following columns:
        'username', 'code', and 'choice'.

    Returns
    -------
    pd.DataFrame
        Deduplicated copy of ``choices`` with at most one row per (username, code) pair.

    """
    return (
        choices.sort_values("choice")
        .drop_duplicates(subset=["username", "code"], keep="first")
        .copy()
    )
