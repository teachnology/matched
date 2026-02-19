import pandas as pd

from .pre_process import deduplicate


def match(choices, nmax):
    """
    Match students to projects.

    The function iteratively matches students to projects based on their choices, the
    maximum number of students accepted per project, and their score. It ensures
    that no project exceeds its maximum capacity and that, for popular projects,
    students with higher scores are given priority.

    Parameters
    ----------
    choices : pd.DataFrame
        DataFrame containing the students' choices and their scores. It must have
        the following columns:

        - ``username``: unique identifier for each student.
        - ``code``: project code the student selected.
        - ``choice``: rank of the preference (1 = first choice, 2 = second choice,
          etc.). Lower numbers take priority during allocation.
        - ``score``: the student's score, used as a tiebreaker when a project is
          oversubscribed (higher score takes priority).
    nmax : pd.Series
        Series containing the maximum number of students allowed for each project. The
        index should be the project code and the value should be the maximum capacity.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the final allocations of students to projects. The index
        is 'username'. Allocated students have columns 'code' (project code) and
        'choice' (the choice number they were allocated). Students who could not be
        allocated have NaN for both columns.

    Raises
    ------
    ValueError
        If data validation fails, such as missing required columns in `choices`.

    """
    # Basic input validation.
    required_cols = {"username", "code", "choice", "score"}
    if missing_cols := required_cols - set(choices.columns):
        raise ValueError(f"'choices' is missing required columns: {missing_cols}")

    if unknown_codes := set(choices.code) - set(nmax.index):
        raise ValueError(
            f"'nmax' does not contain entries for the following project codes: "
            f"{unknown_codes}"
        )

    # Deduplicate (username, code) pairs, keeping the row with the lowest choice
    # number, if any student selected the same project multiple times.
    _original_choices = deduplicate(choices)

    # Store allocations in a dictionary.
    allocations = {}

    remaining = choices.copy()

    while len(remaining) > 0:  # while there are still students to allocate
        # In the first iteration, this will be the first choice. In the second
        # iteration, this will be the second choice, and so on.
        current_round = remaining[remaining.choice.eq(remaining.choice.min())]

        for code in current_round.code.unique():  # go through unique project codes
            # Retrieve maximum number of students that can be allocated to the project.
            nmax_ = nmax.loc[code]

            # Get all students who selected the project and sort them by their score
            # in descending order.
            df_ = current_round[current_round.code.eq(code)].sort_values(
                by="score", ascending=False
            )

            # Allocate students to the project as long as n < nmax.
            for username in df_.username:
                n_allocated = sum(v == code for v in allocations.values())

                if n_allocated < nmax_:  # if the project is not full yet
                    # Allocate the student to the project.
                    allocations[username] = code

                    # Remove the student from the remaining DataFrame since they have
                    # been allocated and their lower choices do not need to be
                    # considered anymore.
                    remaining = remaining[remaining.username.ne(username)]

                # If the project is full, remove it. Other students cannot be allocated
                # to it, and we don't want to consider it in the next iterations.
                elif n_allocated == nmax_:
                    remaining = remaining[remaining.code.ne(code)]
                    break

                else:
                    assert False, (
                        f"Project {code} has more than {nmax_} students allocated "
                        f"({n_allocated}). This should never happen."
                    )

    # Build the result, including students who could not be placed (NaN for code).
    all_usernames = choices.username.unique()
    allocations_series = pd.Series(
        {username: allocations.get(username, pd.NA) for username in all_usernames},
        name="code",
    )

    # Retrieve the choice number for each allocated student by merging with the
    # original choices. Unallocated students (NaN code) will have NaN for choice.
    return (
        allocations_series.to_frame()
        .reset_index(names="username")
        .merge(
            _original_choices[["username", "code", "choice"]],
            on=["username", "code"],
            how="left",
        )
        .set_index("username")
    )


def shortlist(choices, code):
    """
    Return all students who selected the given project code, sorted by score descending.

    Parameters
    ----------
    choices : pd.DataFrame
        DataFrame with at least columns 'username', 'code', and 'score'.
    code : str
        Project code to filter by.

    Returns
    -------
    pd.DataFrame
        Subset of choices for the given project, sorted by score descending.
    """
    return choices[choices.code.eq(code)].sort_values(by="score", ascending=False)
