import pandas as pd
import streamlit as st
from display import (
    display_batting_data,
    display_pitching_data,
    display_player_data,
    display_score_data,
)
from info import team_dict, teams_url


def main():
    team = "ryunen_busters"

    score_df = pd.read_csv(f"data/{team}/score.csv")
    batting_df = pd.read_csv(f"data/{team}/batting.csv")
    pitching_df = pd.read_csv(f"data/{team}/pitching.csv")

    st.title(f"[{team_dict[team]}]({teams_url + team}) 分析アプリ")

    st.sidebar.title("メニュー")
    selected_type = st.sidebar.radio("表示するデータ", ["スコア", "打撃成績", "投手成績", "個人成績"])

    if selected_type == "スコア":
        display_score_data(score_df, team, used_key_num=0)
    elif selected_type == "打撃成績":
        display_batting_data(score_df, batting_df, used_key_num=1)
    elif selected_type == "投手成績":
        display_pitching_data(score_df, pitching_df, used_key_num=2)
    elif selected_type == "個人成績":
        players = batting_df[["背番号", "選手名"]].drop_duplicates()
        players = players[players["背番号"].str.isdigit()]
        players["背番号"] = players["背番号"].astype(int)
        players = players.sort_values("背番号")
        players["表示名"] = players["背番号"].astype(str) + " " + players["選手名"]
        selected_player = st.sidebar.selectbox(
            "選手を選択してください",
            players["表示名"],
        )
        player_number = int(selected_player.split()[0])
        player_name = selected_player.split()[1]
        display_player_data(
            score_df,
            batting_df,
            pitching_df,
            team,
            player_number,
            player_name,
            used_key_num=3,
        )


if __name__ == "__main__":
    main()
