import pandas as pd


def match(choices, nmax):
    """
    Match students to projects.

    The function iteratively allocates students to projects based on their choices, the
    maximum number of students accepted per project and their mean mark. It ensures that
    no project exceeds its maximum capacity and that students are allocated to their
    preferred projects as much as possible.

    Parameters
    ----------
    choices : pd.DataFrame
        DataFrame containing the students' choices and their corresponding mean marks.
        It should have the following columns: 'username', 'code', 'choice', and 'mean'.
    nmax : pd.Series
        Series containing the maximum number of students allowed for each project. The
        index should be the project codes and the values should be the maximum
        capacities.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the final allocations of students to projects. It will have
        the following columns: 'username', 'code', and 'choice'.

    """
    allocations = pd.Series({}, name="code")

    _original_choices = choices.copy()
    choices = choices.copy()

    while len(choices) > 0:
        choice = choices[choices.choice == choices.choice.min()]

        for code in choice.code.unique():  # go through unique projects
            # maximum number of students that can be allocated to the project
            nmax_ = nmax.loc[code]

            df_ = choice[choice.code == code].sort_values(by="mean", ascending=False)

            # Allocate students to the project as long as n < nmax.
            for username in df_.username:
                if allocations.eq(code).sum() < nmax_:
                    allocations.loc[username] = code
                    choices = choices[choices.username != username]

                # If the project is full, remove it.
                elif allocations.eq(code).sum() == nmax_:
                    choices = choices[choices.code != code]
                    break

                elif allocations.eq(code).sum() > nmax_:
                    raise ValueError(
                        f"Project {code} has more than {nmax} students allocated."
                    )

    def _choice(row):
        return _original_choices.loc[
            (_original_choices.username == row.name)
            & (_original_choices.code == row.code),
            "choice",
        ].item()

    allocations = allocations.to_frame().assign(
        choice=lambda df_: df_.apply(_choice, axis=1)
    )

    return allocations
