import argparse

from result import ClosenessResult
from single_pass_strategy import SinglePassStrategy
from utils import filter, guess_result, read_dataset


def main(target: str):
    df = read_dataset()
    target_attributes = df[df["Player"].str.contains(target)].iloc[0]

    solved = False
    filtered_df = df.copy()

    round = 0
    while not solved:
        strat = SinglePassStrategy(filtered_df)

        res = guess_result(strat.guess_row, target_attributes)
        if res.player == ClosenessResult.GREEN:
            break

        filtered_df = filter(
            filtered_df,
            strat.guess_row,
            res
        )

        round += 1
        print(f"Round {round}, Guessed: {strat.guess_row}, Number of possible matches, {len(filtered_df)}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target")
    args = parser.parse_args()
 
    main(args.target)