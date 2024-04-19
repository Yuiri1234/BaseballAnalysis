import datetime

import pandas as pd
import streamlit as st
from calculate import calc_goal_diff, calc_points_losts, win_or_lose
from info import team_dict


def display_score_data(df, team):
    st.write("## 試合結果")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        options = ["すべて", "公式戦", "練習試合"]
        selected_option1 = st.selectbox("フィルタ", options, index=0)
    with col2:
        options = ["すべて", "先攻", "後攻"]
        selected_option2 = st.selectbox("先攻後攻", options, index=0)
    with col3:
        options = ["すべて", "勝ち", "負け", "引き分け"]
        selected_option3 = st.selectbox("結果", options, index=0)
    with col4:
        unique_years = pd.to_datetime(df["game_date"]).dt.year.unique()
        df["game_date"] = pd.to_datetime(df["game_date"])
        options = ["すべて"] + [f"{year}年" for year in unique_years] + ["その他"]
        selected_option4 = st.selectbox("年", options, index=0)

    score_df = df.copy()
    score_df[["points", "losts"]] = score_df.apply(
        lambda row: calc_points_losts(row, team_dict[team]),
        axis=1,
        result_type="expand",
    )
    score_df["goal_diff"] = score_df.apply(
        lambda row: calc_goal_diff(row, team_dict[team]), axis=1
    )
    score_df["result"] = score_df.apply(
        lambda row: win_or_lose(row, team_dict[team]), axis=1
    )
    score_df = score_df[
        [
            "game_type",
            "game_date",
            "team_name_top",
            "team_name_bottom",
            "points",
            "losts",
            "goal_diff",
            "result",
        ]
    ]  # ここで選択する必要はない
    score_df.columns = ["試合種別", "試合日", "先攻", "後攻", "得点", "失点", "得失点差", "試合結果"]

    if selected_option1 == "すべて":
        display_df = score_df
    elif selected_option1 == "公式戦":
        display_df = score_df[score_df["試合種別"] == "公式戦"]
    elif selected_option1 == "練習試合":
        display_df = score_df[score_df["試合種別"] == "練習試合"]

    if selected_option2 == "すべて":
        display_df = display_df
    elif selected_option2 == "先攻":
        display_df = display_df[display_df["先攻"] == team_dict[team]]
    elif selected_option2 == "後攻":
        display_df = display_df[display_df["先攻"] != team_dict[team]]

    if selected_option3 == "すべて":
        display_df = display_df
    elif selected_option3 == "勝ち":
        display_df = display_df[display_df["試合結果"] == "○"]
    elif selected_option3 == "負け":
        display_df = display_df[display_df["試合結果"] == "☓"]
    elif selected_option3 == "引き分け":
        display_df = display_df[display_df["試合結果"] == "△"]

    if selected_option4 == "すべて":
        display_df = display_df
    elif selected_option4 == "その他":
        col1, col2 = st.columns(2)
        with col1:
            selected_date1 = st.date_input(
                "期間 (前)", datetime.datetime.now() - datetime.timedelta(days=30)
            )
            display_df = display_df[display_df["試合日"].dt.date >= selected_date1]
        with col2:
            selected_date2 = st.date_input("期間 (後)", datetime.datetime.now())
            display_df = display_df[display_df["試合日"].dt.date <= selected_date2]
    else:
        year = int(selected_option4.replace("年", ""))
        display_df = display_df[display_df["試合日"].dt.year == year]

    st.write(display_df)  # ここでカラムを選択すればよい
    results = [
        {
            "勝ち": display_df[display_df["試合結果"] == "○"].shape[0],
            "負け": display_df[display_df["試合結果"] == "☓"].shape[0],
            "引き分け": display_df[display_df["試合結果"] == "△"].shape[0],
            "合計得点": display_df["得点"].sum(),
            "合計失点": display_df["失点"].sum(),
            "合計得失点差": display_df["得失点差"].sum(),
            "1試合平均得点": display_df["得点"].mean(),
            "1試合平均失点": display_df["失点"].mean(),
            "1試合平均得失点差": display_df["得失点差"].mean(),
        }
    ]
    results = pd.DataFrame(results)
    results.index = [f"{team_dict[team]}"]
    st.write(results)


def display_batting_data(df):
    st.write("## 打撃成績")
    st.write(df)


def display_pitching_data(df):
    st.write("## 投手成績")
    st.write(df)


def display_player_data(batting_df, pitching_df, player_number, player_name):
    st.write(f"## {player_name} ({player_number})")
    st.write("### 打撃成績")
    batting_df = batting_df[batting_df["選手名"] == player_name]
    st.write(batting_df)
    st.write("### 投手成績")
    pitching_df = pitching_df[pitching_df["選手名"] == player_name]
    st.write(pitching_df)
