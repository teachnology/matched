import pathlib
import random

import fakeitmakeit as fm
import pandas as pd

CWD = pathlib.Path(__file__).parent

if __name__ == "__main__":
    if not pathlib.Path(CWD / "choices.csv").exists():
        cohort = fm.cohort(n=5)
        scores = fm.assignment(usernames=cohort.index, pfail=0.0, pnan=0.0).rename(
            "score"
        )

        codes = [f"code{i}" for i in range(1, 4)]

        sh = cohort.rename(columns={"mark": "score"}).assign(
            c1=random.choices(codes, k=5),
            c2=random.choices(codes, k=5),
            c3=random.choices(codes, k=5),
        )

        choices = (
            pd.melt(
                sh.reset_index(),
                id_vars=["username"],
                value_vars=["c1", "c2", "c3"],
                var_name="choice",
                value_name="code",
            )
            .merge(scores, left_on="username", right_index=True, how="left")
            .assign(
                choice=lambda df_: df_.choice.str.extract(r"(\d)").astype(int),
            )
            .drop_duplicates(
                subset=["username", "code"], keep="first"
            )  # if somebody selected the same project more than once
            .loc[:, ["username", "code", "choice", "score"]]
            .sort_values(by=["username", "choice"])
        )

        choices.to_csv(CWD / "choices.csv", index=False)

    if not pathlib.Path(CWD / "nmax.csv").exists():
        nmax = pd.Series(
            [random.randint(1, 3) for _ in range(3)],
            index=["code1", "code2", "code3"],
            name="nmax",
        )

        nmax.to_csv(CWD / "nmax.csv", index=True)
