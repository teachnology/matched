import pandas as pd


def match(choices, scores, nmax):
    """
    Match students to projects.

    The function iteratively matches students to projects based on their choices, the
    maximum number of students accepted per project, and their score. It ensures
    that no project exceeds its maximum capacity and that, for popular projects,
    students with higher scores are given priority. A student's score only matters
    as a tiebreaker when a project they picked is oversubscribed within the same
    round - it never overrides preference order.

    Parameters
    ----------
    choices : dict[str, list[str]]
        Mapping of username to an ordered list of project codes (rank implied by
        position: index 0 is the student's first choice, etc.).
    scores : dict[str, float]
        Mapping of username to the student's score, used as a tiebreaker when a
        project is oversubscribed (higher score takes priority).
    nmax : dict[str, int]
        Mapping of project code to the maximum number of students it can accept.

    Returns
    -------
    dict[str, str | None]
        Mapping of username to the project code they were allocated to. Every
        username in ``choices`` is present as a key; students who could not be
        allocated map to ``None``.

    Raises
    ------
    ValueError
        If ``scores`` is missing an entry for a username in ``choices``, or if
        ``nmax`` is missing an entry for a project code referenced in ``choices``.

    Examples
    --------
    >>> import matched
    >>> choices = {"alice": ["code1", "code2"], "bob": ["code1"]}
    >>> scores = {"alice": 90, "bob": 70}
    >>> nmax = {"code1": 1, "code2": 1}
    >>> matched.match(choices, scores, nmax)
    {'alice': 'code1', 'bob': None}

    """
    # Basic input validation.
    if missing_usernames := set(choices) - set(scores):
        raise ValueError(
            f"'scores' is missing entries for usernames: {missing_usernames}"
        )

    all_codes = {code for codes in choices.values() for code in codes}
    if unknown_codes := all_codes - set(nmax):
        raise ValueError(
            f"'nmax' does not contain entries for the following project codes: "
            f"{unknown_codes}"
        )

    # Build a "long" DataFrame, one row per (username, code) choice, with the choice
    # rank derived from each student's list position and the score joined in from
    # `scores` - this lets the allocation loop below reuse pandas' vectorized
    # groupby/sort operations instead of looping over plain Python dicts.
    remaining = pd.DataFrame(
        [
            {
                "username": username,
                "code": code,
                "choice": rank,
                "score": scores[username],
            }
            for username, codes in choices.items()
            for rank, code in enumerate(codes, start=1)
        ],
        columns=["username", "code", "choice", "score"],
    )

    nmax_ = pd.Series(nmax)

    # Store allocations in a dictionary.
    allocations = {}

    while len(remaining) > 0:  # while there are still students to allocate
        # In the first iteration, this will be the first choice. In the second
        # iteration, this will be the second choice, and so on.
        current_round = remaining[remaining.choice.eq(remaining.choice.min())]

        for code in current_round.code.unique():  # go through unique project codes
            # Retrieve maximum number of students that can be allocated to the project.
            nmax_code = nmax_.loc[code]

            # Get all students who selected the project and sort them by their score
            # in descending order.
            df_ = current_round[current_round.code.eq(code)].sort_values(
                by="score", ascending=False
            )

            # Allocate students to the project as long as n < nmax.
            for username in df_.username:
                n_allocated = sum(v == code for v in allocations.values())

                if n_allocated < nmax_code:  # if the project is not full yet
                    # Allocate the student to the project.
                    allocations[username] = code

                    # Remove the student from the remaining DataFrame since they have
                    # been allocated and their lower choices do not need to be
                    # considered anymore.
                    remaining = remaining[remaining.username.ne(username)]

                # If the project is full, remove it. Other students cannot be allocated
                # to it, and we don't want to consider it in the next iterations.
                elif n_allocated == nmax_code:
                    remaining = remaining[remaining.code.ne(code)]
                    break

                else:
                    raise AssertionError(
                        f"Project {code} has more than {nmax_code} students allocated "
                        f"({n_allocated}). This should never happen."
                    )

    # Every username from the input appears in the result; unallocated students (no
    # entry in `allocations`) get None.
    return {username: allocations.get(username) for username in choices}


def choice_rank(choices, allocated):
    """
    Look up the choice rank of each student's allocated project.

    Parameters
    ----------
    choices : dict[str, list[str]]
        Mapping of username to an ordered list of project codes, as passed to
        :func:`match`.
    allocated : dict[str, str | None]
        Mapping of username to allocated project code, as returned by :func:`match`.

    Returns
    -------
    dict[str, int | None]
        Mapping of username to the rank (1 = first choice, 2 = second choice, etc.)
        of their allocated project. Students allocated ``None`` map to ``None``.

    Examples
    --------
    >>> import matched
    >>> choices = {"alice": ["code1", "code2"]}
    >>> allocated = {"alice": "code2"}
    >>> matched.choice_rank(choices, allocated)
    {'alice': 2}

    """
    return {
        username: None if code is None else choices[username].index(code) + 1
        for username, code in allocated.items()
    }


def shortlist(choices, scores, code):
    """
    Return all students who selected the given project code, sorted by score descending.

    Parameters
    ----------
    choices : dict[str, list[str]]
        Mapping of username to an ordered list of project codes.
    scores : dict[str, float]
        Mapping of username to the student's score.
    code : str
        Project code to filter by.

    Returns
    -------
    list[str]
        Usernames of students who selected ``code``, sorted by score descending.

    Examples
    --------
    >>> import matched
    >>> choices = {"alice": ["code1"], "bob": ["code2", "code1"]}
    >>> scores = {"alice": 90, "bob": 95}
    >>> matched.shortlist(choices, scores, "code1")
    ['bob', 'alice']

    """
    applicants = [username for username, codes in choices.items() if code in codes]
    return sorted(applicants, key=lambda username: scores[username], reverse=True)
