def deduplicate(choices):
    """
    Deduplicate student project choices.

    For each student, only the first occurrence of a project code in their ordered
    list of choices is kept. This handles the case where a student has selected the
    same project more than once across different preference ranks.

    Parameters
    ----------
    choices : dict[str, list[str]]
        Mapping of username to an ordered list of project codes (rank is implied by
        position: index 0 is the student's first choice, etc.).

    Returns
    -------
    dict[str, list[str]]
        Deduplicated copy of ``choices`` with no repeated project code per username.

    Examples
    --------
    >>> import matched
    >>> matched.deduplicate({"alice": ["code1", "code2", "code1"]})
    {'alice': ['code1', 'code2']}

    """
    # dict.fromkeys drops repeats while preserving first-seen order (i.e. best rank).
    return {username: list(dict.fromkeys(codes)) for username, codes in choices.items()}


def filter_invalid_code(choices, nmax):
    """
    Remove choices with invalid project codes.

    Parameters
    ----------
    choices : dict[str, list[str]]
        Mapping of username to an ordered list of project codes.
    nmax : dict[str, int]
        Mapping of project code to its maximum capacity. Its keys define the set of
        known/valid project codes.

    Returns
    -------
    dict[str, list[str]]
        Filtered copy of ``choices`` containing only project codes present in
        ``nmax``.

    Examples
    --------
    >>> import matched
    >>> matched.filter_invalid_code({"alice": ["code1", "bad"]}, {"code1": 1})
    {'alice': ['code1']}

    """
    # Iterating a dict yields its keys, so this is the set of known project codes.
    valid_codes = set(nmax)
    return {
        username: [code for code in codes if code in valid_codes]
        for username, codes in choices.items()
    }


def filter_invalid_course(choices, courses, eligible_courses):
    """
    Remove invalid project choices based on course eligibility.

    Parameters
    ----------
    choices : dict[str, list[str]]
        Mapping of username to an ordered list of project codes.
    courses : dict[str, str]
        Mapping of username to the student's course.
    eligible_courses : dict[str, list[str]]
        Mapping of project code to the list of courses eligible for that project.

    Returns
    -------
    dict[str, list[str]]
        Filtered copy of ``choices`` containing only project codes eligible for each
        student's course.

    Raises
    ------
    KeyError
        If ``courses`` is missing an entry for a username present in ``choices``.

    Examples
    --------
    >>> import matched
    >>> choices = {"alice": ["code1", "code2"]}
    >>> courses = {"alice": "course1"}
    >>> eligible_courses = {"code1": ["course1"], "code2": ["course2"]}
    >>> matched.filter_invalid_course(choices, courses, eligible_courses)
    {'alice': ['code1']}

    """
    return {
        username: [
            code
            for code in codes
            # .get(code, []) so a code missing from eligible_courses is just
            # treated as eligible for no one, rather than raising a KeyError.
            if courses[username] in eligible_courses.get(code, [])
        ]
        for username, codes in choices.items()
    }
