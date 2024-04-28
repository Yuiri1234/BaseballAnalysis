import argparse
import os
import time
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_game_urls(links, url_header):
    game_urls = []
    for link in links:
        link_text = link.get("href")
        if link_text is None:
            continue
        last_part = link_text.split("/")[-1]
        if last_part.isdigit():
            game_urls.append(url_header + "/" + last_part)
    return game_urls


def get_game_info(soup, game):
    dev_list = soup.find_all("div")
    info = {}
    flag = False
    for dev in dev_list:
        if "gameInfo02" in dev.get("class"):
            game_info = dev.text.split("\n")
            game_info = [item.strip() for item in game_info if item.strip()]
            if len(game_info) == 4:
                info["game_place"] = None
                info["team_name_top"] = game_info[0]
                info["team_name_bottom"] = game_info[3]
            elif len(game_info) == 5:
                info["game_place"] = game_info[3]
                info["team_name_top"] = game_info[0]
                info["team_name_bottom"] = game_info[4]
            if flag:
                break
        if "dateInfo" in dev.get("class"):
            date_info = dev.text.split("\n")
            info["game"] = game
            info["game_type"] = date_info[1]
            date = date_info[2].split("(")
            info["game_date"] = datetime.strptime(date[0], "%Y/%m/%d").date()
            info["game_day"] = date[1][0]
            info["game_time"] = date_info[3][:-1]
            if flag:
                break
            flag = True

    info_df = pd.DataFrame([info])
    return info_df


def get_table_info(table):
    rows = table.find_all("tr")
    data = []
    for row in rows:
        # 行からセルを取得します
        cells = row.find_all(["td", "th"])
        row_data = []
        for cell in cells:
            row_data.append(cell.text.strip())  # セルのテキストを取得してリストに追加します
        data.append(row_data)
    df = pd.DataFrame(data[1:], columns=data[0])
    return df


def get_score_df(df, info_df):
    df.columns = ["team_name", "1", "2", "3", "4", "5", "6", "7", "8", "9", "points"]
    df.index = ["top", "bottom"]
    scores = df.iloc[:, 1:].values.flatten()
    score_df = pd.DataFrame([scores])
    columns = []
    columns.extend(
        [
            str(i) + "_" + j if i < 10 else "points_" + j
            for i in range(1, 11)
            for j in ["top"]
        ]
    )
    columns.extend(
        [
            str(i) + "_" + j if i < 10 else "points_" + j
            for i in range(1, 11)
            for j in ["bottom"]
        ]
    )
    score_df.columns = columns
    score_df = pd.concat([info_df, score_df], axis=1)
    return score_df


def get_stats_df(df, info_df):
    df = df.rename(columns={df.columns[0]: "背番号"})
    df = df.iloc[:-1]
    df["game"] = info_df["game"].values[0]
    df["game_type"] = info_df["game_type"].values[0]
    df["game_date"] = info_df["game_date"].values[0]
    df["game_day"] = info_df["game_day"].values[0]
    df["game_time"] = info_df["game_time"].values[0]
    columns = df.columns[-5:].values
    columns = np.concatenate([columns, df.columns[:-5].values])
    df = df[columns]
    return df


def main(args):
    score_df_list = []
    batting_df_list = []
    pitching_df_list = []

    page = 1
    while True:
        url = (
            f"https://teams.one/teams/{args.team}/game"
            f"?page={page}&search_result%5Bgame_date%5D={args.year}"
            f"&search_result%5Bgame_type%5D=&search_result"
            f"%5Bopponent_team_name%5D=&search_result%5B"
            f"tournament_name%5D=&search_result%5Bis_walk_game%5D="
        )
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        links = soup.find_all("a")

        url_header = url.split("?")[0]
        game_urls = get_game_urls(links, url_header)

        folder = f"{args.team}/{args.year}"
        if not os.path.exists(folder):
            os.makedirs(folder)

        if len(game_urls) == 0:
            break
        for game_url in tqdm(game_urls):
            game = game_url.split("/")[-1]
            if os.path.exists(f"{folder}/{game}"):
                score_df_list.append(
                    pd.read_csv(f"{folder}/{game_url.split('/')[-1]}/score.csv")
                )

                try:
                    batting_df_list.append(
                        pd.read_csv(f"{folder}/{game_url.split('/')[-1]}/batting.csv")
                    )
                    pitching_df_list.append(
                        pd.read_csv(f"{folder}/{game_url.split('/')[-1]}/pitching.csv")
                    )
                except FileNotFoundError as e:
                    print(f"game_url: {game_url}")
                    print(f"error: {e}")
            else:
                time.sleep(3)
                response = requests.get(game_url)
                html_content = response.text
                soup = BeautifulSoup(html_content, "html.parser")
                table_list = soup.find_all("table")
                try:
                    info_df = get_game_info(soup, game)
                    score_df = get_table_info(table_list[0])
                    score_df = get_score_df(score_df, info_df)
                    score_df_list.append(score_df)
                    batting_df = get_table_info(table_list[2])
                    batting_df = get_stats_df(batting_df, info_df)
                    batting_df_list.append(batting_df)
                    pitching_df = get_table_info(table_list[4])
                    pitching_df = get_stats_df(pitching_df, info_df)
                    pitching_df_list.append(pitching_df)
                    os.makedirs(f"{folder}/{game}")
                    score_df.to_csv(f"{folder}/{game}/score.csv", index=False)
                    batting_df.to_csv(f"{folder}/{game}/batting.csv", index=False)
                    pitching_df.to_csv(f"{folder}/{game}/pitching.csv", index=False)
                except IndexError as e:
                    print(f"game_url: {game_url}")
                    print(f"error: {e}")
        page += 1
    try:
        score_df_all = pd.concat(score_df_list, axis=0, ignore_index=True)
        batting_df_all = pd.concat(batting_df_list, axis=0, ignore_index=True)
        pitching_df_all = pd.concat(pitching_df_list, axis=0, ignore_index=True)
        score_df_all.to_csv(f"{folder}/score.csv", index=False)
        batting_df_all.to_csv(f"{folder}/batting.csv", index=False)
        pitching_df_all.to_csv(f"{folder}/pitching.csv", index=False)
    except ValueError:
        print(f"{args.year}年のデータがありません")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", type=str, default="ryunen_busters")
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()
    main(args)
