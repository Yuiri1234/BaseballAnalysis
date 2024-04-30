import pandas as pd
import streamlit as st
from lib.calculate import (
    calc_points_diff,
    get_opponent_team,
    get_teams_url,
    win_or_lose,
)

# from streamlit_gsheets import GSheetsConnection
from lib.display import (
    display_batting_data,
    display_pitching_data,
    display_player_data,
    display_sabermetrics,
    display_score_data,
)
from lib.info import team_dict

st.set_page_config(
    page_title="分析アプリ",
    layout="wide",
    initial_sidebar_state="expanded",
)
pd.set_option("display.max_colwidth", 80)


def main():
    st.title("分析アプリ")

    st.sidebar.title("メニュー")
    team = st.sidebar.selectbox("チームを選択してください", team_dict.values())
    team = [key for key, value in team_dict.items() if value == team][0]
    selected_type = st.sidebar.radio("表示するデータ", ["スコア", "打撃成績", "投手成績", "個人成績", "指標説明"])

    score_df = pd.read_csv(f"data/{team}/score.csv")
    batting_df = pd.read_csv(f"data/{team}/batting.csv")
    pitching_df = pd.read_csv(f"data/{team}/pitching.csv")

    score_df["game_url"] = score_df["game"].apply(get_teams_url, team=team)
    score_df["oppo_team"] = score_df.apply(
        lambda row: get_opponent_team(row, team_dict[team]), axis=1
    )
    score_df["game_date"] = pd.to_datetime(score_df["game_date"])
    score_df["result"] = score_df.apply(
        lambda row: win_or_lose(row, team_dict[team]), axis=1
    )
    score_df["points_diff"] = score_df.apply(
        lambda row: calc_points_diff(row, team_dict[team]), axis=1
    )

    if selected_type == "スコア":
        display_score_data(score_df, team, used_key_num=0)
    elif selected_type == "打撃成績":
        display_batting_data(score_df, batting_df, team, used_key_num=1)
    elif selected_type == "投手成績":
        display_pitching_data(score_df, pitching_df, team, used_key_num=2)
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
    elif selected_type == "指標説明":
        display_sabermetrics()


if __name__ == "__main__":
    main()
