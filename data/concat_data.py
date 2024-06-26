import argparse
import os
from glob import glob

import pandas as pd


def main(args):
    folder = f"{args.team}"
    if not os.path.exists(folder):
        print(f"folder: {folder} does not exist")
        return 1

    score_df_list = []
    batting_df_list = []
    pitching_df_list = []

    for year in range(args.last_year, args.first_year, -1):
        files = glob(f"{folder}/{year}/*")
        for file in files:
            filename = file.split("/")[-1].split(".")[0]
            if filename == "score":
                score_df_list.append(pd.read_csv(file))
            elif filename == "batting":
                batting_df_list.append(pd.read_csv(file))
            elif filename == "pitching":
                pitching_df_list.append(pd.read_csv(file))
    score_df_all = pd.concat(score_df_list, axis=0, ignore_index=True)
    batting_df_all = pd.concat(batting_df_list, axis=0, ignore_index=True)
    pitching_df_all = pd.concat(pitching_df_list, axis=0, ignore_index=True)

    score_df_all.to_csv(f"{folder}/score.csv", index=False)
    batting_df_all.to_csv(f"{folder}/batting.csv", index=False)
    pitching_df_all.to_csv(f"{folder}/pitching.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", type=str, default="ryunen_busters")
    parser.add_argument("--first-year", type=int, default=2020)
    parser.add_argument("--last-year", type=int, default=2025)
    args = parser.parse_args()
    main(args)
