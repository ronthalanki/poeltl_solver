import pandas as pd
import numpy as np


dataset_path = "df.csv"
team_dataset_path = "team.csv"

def read_dataset() -> pd.DataFrame:
    df = pd.read_csv("~/dev/poeltl/df.csv")
    team_df = pd.read_csv("~/dev/poeltl/team.csv")
    dataset = pd.merge(df, team_df, left_on="Team", right_on="Team")

    dataset["Age"] = np.floor(dataset["Age"]).astype(int)
    dataset["Height"] = [__get_height_in_inches(height_str) for height_str in df["Height"]]

    return dataset

def __get_height_in_inches(height_str: str) -> int:
    return int(height_str.split('-')[0]) * 12 + int(height_str.split('-')[1])
