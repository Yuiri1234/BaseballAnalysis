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


def calc_win_rate(df):
    win = df[df["result"] == "○"].shape[0]
    lose = df[df["result"] == "☓"].shape[0]
    return win / (win + lose)


def split_inning(inning):
    inning = inning.split("回")
    return pd.Series([int(inning[0]), int(inning[1].split("/")[0])])


def display_filter_options(df):
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
        options = ["すべて"] + [f"{year}年" for year in unique_years] + ["その他"]
        selected_option4 = st.selectbox("年", options, index=0)
    return selected_option1, selected_option2, selected_option3, selected_option4


def display_filter_calendar(df, key1="selected_date1", key2="selected_date2"):
    col1, col2 = st.columns(2)
    with col1:
        selected_date1 = st.date_input(
            "期間 (前)", datetime.datetime.now() - datetime.timedelta(days=30), key=key1
        )
    with col2:
        selected_date2 = st.date_input("期間 (後)", datetime.datetime.now(), key=key2)

    return df[
        (df["game_date"].dt.date >= selected_date1)
        & (df["game_date"].dt.date <= selected_date2)
    ]


def display_filtered_df(
    df,
    team,
    selected_option1,
    selected_option2,
    selected_option3,
    selected_option4,
    used_key_num,
):
    if selected_option1 == "すべて":
        display_df = df
    elif selected_option1 == "公式戦":
        display_df = df[df["game_type"] == "公式戦"]
    elif selected_option1 == "練習試合":
        display_df = df[df["game_type"] == "練習試合"]

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
        key1 = f"selected_date_{used_key_num}_1"
        key2 = f"selected_date_{used_key_num}_2"
        display_df = display_filter_calendar(display_df, key1, key2)
    else:
        year = int(selected_option4.replace("年", ""))
        display_df = display_df[display_df["game_date"].dt.year == year]
    return display_df


def display_score_data(df, team, used_key_num):
    st.write("## 試合結果")

    # フィルタリング
    (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
    ) = display_filter_options(df)

    # 計算
    score_df = df.copy()
    score_df["game_date"] = pd.to_datetime(score_df["game_date"])
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

    display_df = display_filtered_df(
        score_df,
        team,
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        used_key_num,
    )

    results = [
        {
            "勝ち": display_df[display_df["result"] == "○"].shape[0],
            "負け": display_df[display_df["result"] == "☓"].shape[0],
            "引き分け": display_df[display_df["result"] == "△"].shape[0],
            "勝率": calc_win_rate(display_df),
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


def display_batting_data(score_df, batting_df, used_key_num):
    # 計算

    # 表示
    score_df = score_df.rename(columns=column_name)
    batting_df = batting_df.rename(columns=column_name)
    st.write("## 打撃成績")
    st.write(batting_df)


def display_pitching_data(score_df, pitching_df, used_key_num):
    # 計算

    # 表示
    score_df = score_df.rename(columns=column_name)
    pitching_df = pitching_df.rename(columns=column_name)
    st.write("## 投手成績")
    st.write(pitching_df)


def display_player_data(
    score_df, batting_df, pitching_df, team, player_number, player_name, used_key_num
):
    st.write(f"## {player_name} ({player_number})")

    # フィルタリング
    (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
    ) = display_filter_options(batting_df)

    # 計算
    score_df["game_date"] = pd.to_datetime(score_df["game_date"])
    batting_df["game_date"] = pd.to_datetime(batting_df["game_date"])
    pitching_df["game_date"] = pd.to_datetime(pitching_df["game_date"])

    score_df["result"] = score_df.apply(
        lambda row: win_or_lose(row, team_dict[team]), axis=1
    )

    batting_df = pd.merge(
        score_df, batting_df, on=["game_type", "game_date", "game_day", "game_time"]
    )
    pitching_df = pd.merge(
        score_df, pitching_df, on=["game_type", "game_date", "game_day", "game_time"]
    )

    batting_df = display_filtered_df(
        batting_df,
        team,
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        used_key_num=f"{used_key_num}_0",
    )
    batting_df = batting_df[batting_df["選手名"] == player_name]
    total_bases = (
        batting_df["安打"].sum()
        + batting_df["二塁打"].sum()
        + batting_df["三塁打"].sum() * 2
        + batting_df["本"].sum() * 3
    )

    try:
        on_base_percentage = (batting_df["安打"].sum() + batting_df["四死球"].sum()) / (
            batting_df["打数"].sum() + batting_df["四死球"].sum() + batting_df["犠飛"].sum()
        )
        slugging_percentage = total_bases / batting_df["打数"].sum()
        average = batting_df["安打"].sum() / batting_df["打数"].sum()
    except ZeroDivisionError:
        on_base_percentage = None
        slugging_percentage = None
        average = None

    batting_result = [
        {
            "試合数": batting_df.shape[0],
            "打率": average,
            "打席": batting_df["打席"].sum(),
            "打数": batting_df["打数"].sum(),
            "安打": batting_df["安打"].sum(),
            "本塁打": batting_df["本"].sum(),
            "打点": batting_df["打点"].sum(),
            "得点": batting_df["得点"].sum(),
            "盗塁": batting_df["盗塁"].sum(),
            "出塁率": on_base_percentage,
            "長打率": slugging_percentage,
            "OPS": on_base_percentage + slugging_percentage,
            "二塁打": batting_df["二塁打"].sum(),
            "三塁打": batting_df["三塁打"].sum(),
            "塁打数": total_bases,
            "三振": batting_df["三振"].sum(),
            "四死球": batting_df["四死球"].sum(),
            "犠打": batting_df["犠打"].sum(),
            "犠飛": batting_df["犠飛"].sum(),
            "併殺打": batting_df["併殺打"].sum(),
            "敵失": batting_df["敵失"].sum(),
            "失策": batting_df["失策"].sum(),
        }
    ]
    batting_result = pd.DataFrame(batting_result)
    batting_result.index = [f"{player_name}"]

    # 表示
    st.write("### 打撃成績")

    batting_df = batting_df.rename(columns=column_name)
    batting_df["試合日"] = batting_df["試合日"].dt.strftime("%Y/%m/%d")
    st.write(
        batting_df[
            [
                "背番号",
                "選手名",
                "試合種別",
                "試合日",
                "結果",
                "出場",
                "打順",
                "守備",
                "打席",
                "打数",
                "安打",
                "本",
                "打点",
                "得点",
                "盗塁",
                "二塁打",
                "三塁打",
                "三振",
                "四死球",
                "犠打",
                "犠飛",
                "併殺打",
                "敵失",
                "失策",
            ]
        ]
    )
    st.write(batting_result)

    st.write("### 投手成績")

    pitching_df = display_filtered_df(
        pitching_df,
        team,
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        used_key_num=f"{used_key_num}_1",
    )
    pitching_df = pitching_df[pitching_df["選手名"] == player_name]
    try:
        pitching_df[["投球回(フル)", "投球回(1/3)"]] = pitching_df["投球回"].apply(split_inning)
    except Exception:
        pitching_df[["投球回(フル)", "投球回(1/3)"]] = pd.DataFrame(
            [[0, 0]], index=pitching_df.index
        )
    try:
        win_rate = pitching_df[pitching_df["勝敗"] == "勝"].shape[0] / (
            pitching_df[pitching_df["勝敗"] == "勝"].shape[0]
            + pitching_df[pitching_df["勝敗"] == "負"].shape[0]
        )
        sum_inning = pitching_df["投球回(フル)"].sum() + pitching_df["投球回(1/3)"].sum() / 3
        diffence_rate = (pitching_df["自責点"].sum() / sum_inning * 7,)  # 7回で1試合
    except ZeroDivisionError:
        win_rate = None
        sum_inning = 0
        diffence_rate = None
    sum_inning_str = (
        f"{pitching_df['投球回(フル)'].sum() + pitching_df['投球回(1/3)'].sum() // 3}回",
        f"{pitching_df['投球回(1/3)'].sum() % 3}/3",
    )

    pitching_result = [
        {
            "試合数": pitching_df.shape[0],
            "勝": pitching_df[pitching_df["勝敗"] == "勝"].shape[0],
            "負": pitching_df[pitching_df["勝敗"] == "負"].shape[0],
            "勝率": win_rate,
            "防御率": diffence_rate,
            "投球回": sum_inning_str,
            "失点": pitching_df["失点"].sum(),
            "自責点": pitching_df["自責点"].sum(),
            "完投": pitching_df[pitching_df["完投"] == "◯"].shape[0],
            "完封": pitching_df[pitching_df["完封"] == "◯"].shape[0],
            "被安打": pitching_df["被安打"].sum(),
            "被本塁打": pitching_df["被本塁打"].sum(),
            "奪三振": pitching_df["奪三振"].sum(),
            "与四死球": pitching_df["与四死球"].sum(),
            "ボーク": pitching_df["ボーク"].sum(),
            "暴投": pitching_df["暴投"].sum(),
        }
    ]
    pitching_result = pd.DataFrame(pitching_result)
    pitching_result.index = [f"{player_name}"]

    # 表示
    pitching_df = pitching_df.rename(columns=column_name)
    pitching_df["試合日"] = pitching_df["試合日"].dt.strftime("%Y/%m/%d")
    st.write(
        pitching_df[
            [
                "背番号",
                "選手名",
                "試合種別",
                "試合日",
                "結果",
                "勝敗",
                "投球回",
                "失点",
                "自責点",
                "完投",
                "完封",
                "被安打",
                "被本塁打",
                "奪三振",
                "与四死球",
                "ボーク",
                "暴投",
                "登板順",
            ]
        ]
    )
    st.write(pitching_result)
