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


def filter_invalid_course(choices, projects):
    """
    Remove invalid project choices based on course eligibility.

    Parameters
    ----------
    choices : pd.DataFrame
        DataFrame with at least columns 'username', 'code', and 'course'.
    projects : pd.DataFrame
        DataFrame with project codes as index and boolean columns for each course (e.g.,
        'course1', 'course2', ...), indicating project eligibility for each course.

    Returns
    -------
    pd.DataFrame
        Filtered choices DataFrame with only valid (course, project) pairs.
    """
    # For each row, check if the project is available to the student's course
    mask = choices.apply(lambda row: projects.loc[row.code, row.course], axis=1)
    return choices[mask].copy()


def filter_invalid_code(choices, valid_codes):
    """
    Remove choices with invalid project codes.

    Parameters
    ----------
    choices : pd.DataFrame
        DataFrame with at least a 'code' column representing project codes.
    valid_codes : iterable
        Valid project codes.

    Returns
    -------
    pd.DataFrame
        Filtered choices DataFrame containing only rows with valid project codes.
    """
    return choices[choices.code.isin(valid_codes)].copy()
