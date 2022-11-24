import pandas as pd
import numpy as np
import re
from typing import Any, Tuple

from result import ClosenessResult, Result, UpDownResult

dataset_path = "df.csv"
team_dataset_path = "team.csv"

def read_dataset() -> pd.DataFrame:
    df = pd.read_csv("~/dev/poeltl/df.csv")
    team_df = pd.read_csv("~/dev/poeltl/team.csv")
    dataset = pd.merge(df, team_df, left_on="Team", right_on="Team")

    dataset["Age"] = np.floor(dataset["Age"]).astype(int)
    dataset["Height"] = [__get_height_in_inches(height_str) for height_str in df["Height"]]
    dataset["No"] = dataset["No"].astype(int)

    return dataset


def __get_height_in_inches(height_str: str) -> int:
    return int(height_str.split('-')[0]) * 12 + int(height_str.split('-')[1])


def guess_result(predict: pd.Series, actual: pd.Series) -> Result:
    def exact_match(actual: Any, predict: Any) -> ClosenessResult:
        if actual == predict:
            return ClosenessResult.GREEN
        return ClosenessResult.GRAY

    player_result = exact_match(actual["Player"], predict["Player"])
    conference_result = exact_match(actual["Conference"], predict["Conference"])
    division_result = exact_match(actual["Division"], predict["Division"])
    team_result = exact_match(actual["Team"], predict["Team"])

    position_result = exact_match(actual["Position"], predict["Position"])
    if position_result != ClosenessResult.GREEN:
        actual_position_array = set(actual["Position"].split("-"))
        predict_position_array = set(predict["Position"].split("-"))

        intersection = actual_position_array.intersection(predict_position_array)
        if intersection:
            position_result = ClosenessResult.YELLOW
        else:
            position_result = ClosenessResult.GRAY


    def approximate_match(actual: int, predict: int) -> Tuple[ClosenessResult, UpDownResult]:
        difference = predict - actual 

        if difference == 0:
            return (ClosenessResult.GREEN, UpDownResult.NEITHER)
        
        if abs(difference) <= 2: 
            closeness_result = ClosenessResult.YELLOW
        else:
            closeness_result = ClosenessResult.GRAY

        if difference < 0:
            updown_result = UpDownResult.UP
        else:
            updown_result = UpDownResult.DOWN
        
        
        return closeness_result, updown_result
    
    age_result = approximate_match(actual["Age"], predict["Age"])
    no_result = approximate_match(actual["No"], predict["No"])
    height_result = approximate_match(actual["Height"], predict["Height"])

    return Result(
        player_result, conference_result, division_result, team_result, position_result,
        age_result, no_result, height_result
    )


def filter(
    df: pd.DataFrame, 
    guess: pd.Series, 
    result: Result
):
    def exact_filter(df: pd.DataFrame, column_name: str, closeness_result: ClosenessResult) -> pd.DataFrame:
        assert closeness_result != ClosenessResult.YELLOW
        if closeness_result == ClosenessResult.GREEN:
            return df[df[column_name] == guess[column_name]]
        elif closeness_result == ClosenessResult.GRAY:
            return df[df[column_name] != guess[column_name]]

    df = exact_filter(df, "Player", result.player)
    df = exact_filter(df, "Conference", result.conference)
    df = exact_filter(df, "Division", result.division)
    df = exact_filter(df, "Team", result.team)


    positions_regex = re.sub("-", "|", guess["Position"])
    if result.position == ClosenessResult.GREEN:
        df = df[df["Position"] == guess["Position"]]
    elif result.position == ClosenessResult.YELLOW:
        df = df[df["Position"].str.contains(positions_regex)]
    elif result.position == ClosenessResult.GRAY:
        df = df[~df["Position"].str.contains(positions_regex)]


    def approximate_filter(df: pd.DataFrame, column_name: str, closeness_result: ClosenessResult, updown_result: UpDownResult) -> pd.DataFrame:
        if closeness_result == ClosenessResult.GREEN:
            return df[df[column_name] == guess[column_name]]

        if updown_result == UpDownResult.DOWN:
            df = df[df[column_name] < guess[column_name]]
        elif result.age[1] == UpDownResult.UP:
            df = df[df[column_name] > guess[column_name]]
        
        if closeness_result == ClosenessResult.YELLOW:
            df = df[abs(df[column_name] - guess[column_name]) <= 2]
        elif closeness_result == ClosenessResult.GRAY:
            df = df[abs(df[column_name] - guess[column_name]) > 2]
        
        return df

    df = approximate_filter(df, "Age", result.age[0], result.age[1])
    df = approximate_filter(df, "Height", result.height[0], result.height[1])
    
    return df