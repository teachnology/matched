import pandas as pd


def match(choices, nmax):
    """
    Match students to projects.

    The function iteratively matches students to projects based on their choices, the
    maximum number of students accepted per project, and their mean mark. It ensures
    that no project exceeds its maximum capacity and that, for popular projects,
    students with higher mean marks are given priority.

    Parameters
    ----------
    choices : pd.DataFrame
        DataFrame containing the students' choices and their mean marks. It must have
        the following columns:

        - ``username``: unique identifier for each student.
        - ``code``: project code the student selected.
        - ``choice``: rank of the preference (1 = first choice, 2 = second choice,
          etc.). Lower numbers take priority during allocation.
        - ``mean``: the student's mean mark, used as a tiebreaker when a project is
          oversubscribed (higher mean takes priority).
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
    required_cols = {"username", "code", "choice", "mean"}
    if missing_cols := required_cols - set(choices.columns):
        raise ValueError(f"'choices' is missing required columns: {missing_cols}")

    if unknown_codes := set(choices.code) - set(nmax.index):
        raise ValueError(
            f"'nmax' does not contain entries for the following project codes: "
            f"{unknown_codes}"
        )

    # Deduplicate (username, code) pairs, keeping the row with the lowest choice number,
    # if any student selected the same project multiple times.
    _original_choices = (
        choices.sort_values("choice")
        .drop_duplicates(subset=["username", "code"], keep="first")
        .copy()  # copy to avoid modifying choices DataFrame outside of this function.
    )

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

            # Get all students who selected the project and sort them by their mean mark
            # in descending order.
            df_ = current_round[current_round.code.eq(code)].sort_values(
                by="mean", ascending=False
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

    # Retrieve the choice number for each allocated student for later data analysis.
    def _choice(row):
        if pd.isna(row.code):
            return pd.NA

        return _original_choices.loc[
            _original_choices.username.eq(row.name)
            & _original_choices.code.eq(row.code),
            "choice",
        ].item()

    return allocations_series.to_frame().assign(
        choice=lambda df_: df_.apply(_choice, axis=1)
    )
