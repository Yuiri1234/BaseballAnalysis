import datetime

import pandas as pd
import streamlit as st
from calculate import (
    calc_inning_losts,
    calc_inning_points,
    calc_points_diff,
    calc_points_losts,
    win_or_lose,
)
from info import column_name, team_dict


def calc_inning_data(df, type="points", calc="sum"):
    if calc == "sum":
        return {
            "1回": df[f"1_{type}"].sum(),
            "2回": df[f"2_{type}"].sum(),
            "3回": df[f"3_{type}"].sum(),
            "4回": df[f"4_{type}"].sum(),
            "5回": df[f"5_{type}"].sum(),
            "6回": df[f"6_{type}"].sum(),
            "7回": df[f"7_{type}"].sum(),
            "8回": df[f"8_{type}"].sum(),
            "9回": df[f"9_{type}"].sum(),
            "合計": df[f"{type}"].sum(),
        }
    elif calc == "mean":
        return {
            "1回": df[f"1_{type}"].mean(),
            "2回": df[f"2_{type}"].mean(),
            "3回": df[f"3_{type}"].mean(),
            "4回": df[f"4_{type}"].mean(),
            "5回": df[f"5_{type}"].mean(),
            "6回": df[f"6_{type}"].mean(),
            "7回": df[f"7_{type}"].mean(),
            "8回": df[f"8_{type}"].mean(),
            "9回": df[f"9_{type}"].mean(),
            "合計": df[f"{type}"].mean(),
        }


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
    score_df["points_diff"] = score_df.apply(
        lambda row: calc_points_diff(row, team_dict[team]), axis=1
    )
    score_df["result"] = score_df.apply(
        lambda row: win_or_lose(row, team_dict[team]), axis=1
    )
    score_df[[f"{i}_points" for i in range(1, 10)]] = score_df.apply(
        lambda row: calc_inning_points(row, team_dict[team]),
        axis=1,
    )
    score_df[[f"{i}_losts" for i in range(1, 10)]] = score_df.apply(
        lambda row: calc_inning_losts(row, team_dict[team]),
        axis=1,
    )

    if selected_option1 == "すべて":
        display_df = score_df
    elif selected_option1 == "公式戦":
        display_df = score_df[score_df["game_type"] == "公式戦"]
    elif selected_option1 == "練習試合":
        display_df = score_df[score_df["game_type"] == "練習試合"]

    if selected_option2 == "すべて":
        display_df = display_df
    elif selected_option2 == "先攻":
        display_df = display_df[display_df["team_name_top"] == team_dict[team]]
    elif selected_option2 == "後攻":
        display_df = display_df[display_df["team_name_top"] != team_dict[team]]

    if selected_option3 == "すべて":
        display_df = display_df
    elif selected_option3 == "勝ち":
        display_df = display_df[display_df["result"] == "○"]
    elif selected_option3 == "負け":
        display_df = display_df[display_df["result"] == "☓"]
    elif selected_option3 == "引き分け":
        display_df = display_df[display_df["result"] == "△"]

    if selected_option4 == "すべて":
        display_df = display_df
    elif selected_option4 == "その他":
        col1, col2 = st.columns(2)
        with col1:
            selected_date1 = st.date_input(
                "期間 (前)", datetime.datetime.now() - datetime.timedelta(days=30)
            )
            display_df = display_df[display_df["game_date"].dt.date >= selected_date1]
        with col2:
            selected_date2 = st.date_input("期間 (後)", datetime.datetime.now())
            display_df = display_df[display_df["game_date"].dt.date <= selected_date2]
    else:
        year = int(selected_option4.replace("年", ""))
        display_df = display_df[display_df["game_date"].dt.year == year]

    results = [
        {
            "勝ち": display_df[display_df["result"] == "○"].shape[0],
            "負け": display_df[display_df["result"] == "☓"].shape[0],
            "引き分け": display_df[display_df["result"] == "△"].shape[0],
            "合計得点": display_df["points"].sum(),
            "合計失点": display_df["losts"].sum(),
            "合計得失点差": display_df["points_diff"].sum(),
            "1試合平均得点": display_df["points"].mean(),
            "1試合平均失点": display_df["losts"].mean(),
            "1試合平均得失点差": display_df["points_diff"].mean(),
        }
    ]
    results = pd.DataFrame(results)
    results.index = [f"{team_dict[team]}"]

    inning_score = [
        calc_inning_data(display_df, type="points", calc="sum"),
        calc_inning_data(display_df, type="points", calc="mean"),
        calc_inning_data(display_df, type="losts", calc="sum"),
        calc_inning_data(display_df, type="losts", calc="mean"),
    ]
    inning_score = pd.DataFrame(inning_score)
    inning_score.index = ["合計得点", "平均得点", "失点", "平均失点"]

    # 表示
    _display_df = display_df.rename(columns=column_name)
    _display_df["試合日"] = _display_df["試合日"].dt.strftime("%Y/%m/%d")
    st.write(
        _display_df[
            [
                "試合種別",
                "試合日",
                "曜日",
                "先攻",
                "後攻",
                "得点",
                "失点",
                "得失点差",
                "結果",
            ]
        ]
    )
    st.write(results)
    st.write(inning_score)


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
