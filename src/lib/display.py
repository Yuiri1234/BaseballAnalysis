import datetime

import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from lib.calculate import (
    calc_inning_losts,
    calc_inning_points,
    calc_points_diff,
    calc_points_losts,
    get_opponent_team,
    get_teams_url,
    win_or_lose,
)
from lib.info import (
    batting_format,
    column_name,
    display_batting_columns,
    display_pitching_columns,
    display_score_columns,
    pitching_format,
    position_list,
    score_format,
    team_dict,
)
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

cm = sns.light_palette("seagreen", as_cmap=True)


def calc_inning_data(df, type="points", calc="mean"):
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
        }


def calc_win_rate(df):
    win = df[df["result"] == "○"].shape[0]
    lose = df[df["result"] == "☓"].shape[0]
    try:
        return win / (win + lose)
    except ZeroDivisionError:
        return None


def calc_score_data(_scene_df, team):
    return {
        "勝ち": _scene_df[_scene_df["result"] == "○"].shape[0],
        "負け": _scene_df[_scene_df["result"] == "☓"].shape[0],
        "引き分け": _scene_df[_scene_df["result"] == "△"].shape[0],
        "勝率": calc_win_rate(_scene_df),
        "合計得点": _scene_df["points"].sum(),
        "合計失点": _scene_df["losts"].sum(),
        "合計得失点差": _scene_df["points_diff"].sum(),
        "1試合平均得点": _scene_df["points"].mean(),
        "1試合平均失点": _scene_df["losts"].mean(),
        "1試合平均得失点差": _scene_df["points_diff"].mean(),
    }


def calc_batting_data(_batting_df):
    total_bases = (
        _batting_df["安打"].sum()
        + _batting_df["二塁打"].sum()
        + _batting_df["三塁打"].sum() * 2
        + _batting_df["本"].sum() * 3
    )

    try:
        on_base_percentage = (_batting_df["安打"].sum() + _batting_df["四死球"].sum()) / (
            _batting_df["打数"].sum() + _batting_df["四死球"].sum() + _batting_df["犠飛"].sum()
        )
        slugging_percentage = total_bases / _batting_df["打数"].sum()
        average = _batting_df["安打"].sum() / _batting_df["打数"].sum()
    except ZeroDivisionError:
        on_base_percentage = None
        slugging_percentage = None
        average = None

    bb_k = (
        _batting_df["四死球"].sum() / _batting_df["三振"].sum()
        if _batting_df["三振"].sum() != 0
        else 99.999
    )

    one_base_hit = (
        _batting_df["安打"].sum()
        - _batting_df["二塁打"].sum()
        - _batting_df["三塁打"].sum()
        - _batting_df["本"].sum()
    )

    try:
        woba_basic = (
            0.7 * (_batting_df["四死球"].sum())
            + 0.9 * (one_base_hit + _batting_df["敵失"].sum())
            + 1.3 * (_batting_df["二塁打"].sum() + _batting_df["三塁打"].sum())
            + 2.0 * _batting_df["本"].sum()
        ) / (_batting_df["打席"].sum() - _batting_df["犠打"].sum())
    except ZeroDivisionError:
        woba_basic = 99.999

    return {
        "背番号": _batting_df["背番号"].values[0],
        "試合数": _batting_df.shape[0],
        "打率": average,
        "打席": _batting_df["打席"].sum(),
        "打数": _batting_df["打数"].sum(),
        "安打": _batting_df["安打"].sum(),
        "二塁打": _batting_df["二塁打"].sum(),
        "三塁打": _batting_df["三塁打"].sum(),
        "本塁打": _batting_df["本"].sum(),
        "打点": _batting_df["打点"].sum(),
        "得点": _batting_df["得点"].sum(),
        "盗塁": _batting_df["盗塁"].sum(),
        "出塁率": on_base_percentage,
        "塁打数": total_bases,
        "長打率": slugging_percentage,
        "OPS": on_base_percentage + slugging_percentage,
        "IsoP": slugging_percentage - average,  # 純長打率
        "IsoD": on_base_percentage - average,
        "wOBA": woba_basic,
        "三振": _batting_df["三振"].sum(),
        "K%": _batting_df["三振"].sum() / _batting_df["打席"].sum(),
        "四死球": _batting_df["四死球"].sum(),
        "BB%": _batting_df["四死球"].sum() / _batting_df["打席"].sum(),
        "BB/K": bb_k,
        "犠打": _batting_df["犠打"].sum(),
        "犠飛": _batting_df["犠飛"].sum(),
        "併殺打": _batting_df["併殺打"].sum(),
        "敵失": _batting_df["敵失"].sum(),
        "失策": _batting_df["失策"].sum(),
    }


def calc_pitching_data(_pitching_df):
    try:
        _pitching_df[["投球回(フル)", "投球回(1/3)"]] = _pitching_df["投球回"].apply(split_inning)
    except Exception:
        _pitching_df[["投球回(フル)", "投球回(1/3)"]] = pd.DataFrame(
            [[0, 0]], index=_pitching_df.index
        )
    try:
        win_rate = _pitching_df[_pitching_df["勝敗"] == "勝"].shape[0] / (
            _pitching_df[_pitching_df["勝敗"] == "勝"].shape[0]
            + _pitching_df[_pitching_df["勝敗"] == "負"].shape[0]
        )
    except ZeroDivisionError:
        win_rate = None
    try:
        sum_inning = _pitching_df["投球回(フル)"].sum() + _pitching_df["投球回(1/3)"].sum() / 3
        if sum_inning == 0:
            diffence_rate = None
        else:
            diffence_rate = _pitching_df["自責点"].sum() / sum_inning * 7  # 7回で1試合
    except ZeroDivisionError:
        sum_inning = 0
        diffence_rate = None
    sum_inning_str = (
        f"{_pitching_df['投球回(フル)'].sum() + _pitching_df['投球回(1/3)'].sum() // 3}回",
        f"{_pitching_df['投球回(1/3)'].sum() % 3}/3",
    )
    return {
        "背番号": _pitching_df["背番号"].values[0],
        "試合数": _pitching_df.shape[0],
        "勝": _pitching_df[_pitching_df["勝敗"] == "勝"].shape[0],
        "負": _pitching_df[_pitching_df["勝敗"] == "負"].shape[0],
        "勝率": win_rate,
        "防御率": diffence_rate,
        "投球回": sum_inning_str,
        "失点": _pitching_df["失点"].sum(),
        "自責点": _pitching_df["自責点"].sum(),
        "完投": _pitching_df[_pitching_df["完投"] == "◯"].shape[0],
        "完封": _pitching_df[_pitching_df["完封"] == "◯"].shape[0],
        "被安打": _pitching_df["被安打"].sum(),
        "被本塁打": _pitching_df["被本塁打"].sum(),
        "奪三振": _pitching_df["奪三振"].sum(),
        "与四死球": _pitching_df["与四死球"].sum(),
        "ボーク": _pitching_df["ボーク"].sum(),
        "暴投": _pitching_df["暴投"].sum(),
    }


def split_inning(inning):
    inning = inning.split("回")
    return pd.Series([int(inning[0]), int(inning[1].split("/")[0])])


def display_filter_options(df):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        options = ["すべて", "公式戦", "練習試合"]
        selected_option1 = st.selectbox("試合種別", options, index=0)
    with col2:
        options = ["すべて", "先攻", "後攻"]
        selected_option2 = st.selectbox("先攻後攻", options, index=0)
    with col3:
        options = ["すべて", "勝ち", "負け", "引き分け"]
        selected_option3 = st.selectbox("結果", options, index=0)
    with col4:
        unique_years = pd.to_datetime(df["game_date"]).dt.year.unique()
        unique_months = np.sort(pd.to_datetime(df["game_date"]).dt.month.unique())
        options = (
            ["すべて"]
            + [f"{year}年" for year in unique_years]
            + [f"{month}月" for month in unique_months]
            + ["直近5試合", "直近10試合", "その他"]
        )
        selected_option4 = st.selectbox("期間", options, index=0)
    with col5:
        unique_oppo_teams = df["oppo_team"].unique()
        options = ["すべて"] + list(unique_oppo_teams)
        selected_option5 = st.selectbox("対戦相手", options, index=0)
    return (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
    )


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


def display_filter_batting_all(df):
    col1, col2, col3 = st.columns(3)
    with col1:
        regulation = st.number_input("規定通算打席数", 0, 100, 30)
    with col2:
        unique_order = list(df["打順"].unique())
        unique_order = [int(i) for i in unique_order if i not in ["-"]]
        unique_order = np.sort(unique_order)
        options = ["すべて"] + [f"{i}番" for i in unique_order]
        order = st.selectbox("打順", options, index=0)
    with col3:
        unique_positions = list(df["守備"].unique())
        unique_positions = [pos for pos in unique_positions if pos not in ["-"]]
        unique_positions = sorted(unique_positions, key=sort_key)
        options = ["すべて"] + [pos for pos in unique_positions]
        position = st.selectbox("守備", options, index=0)
    return regulation, order, position, unique_order, unique_positions


def display_filter_batting(df):
    col1, col2 = st.columns(2)
    with col1:
        unique_order = list(df["打順"].unique())
        unique_order = [int(i) for i in unique_order if i not in ["-"]]
        unique_order = np.sort(unique_order)
        options = ["すべて"] + [f"{i}番" for i in unique_order]
        order = st.selectbox("打順", options, index=0)
    with col2:
        unique_positions = list(df["守備"].unique())
        unique_positions = [pos for pos in unique_positions if pos not in ["-"]]
        unique_positions = sorted(unique_positions, key=sort_key)
        options = ["すべて"] + [pos for pos in unique_positions]
        position = st.selectbox("守備", options, index=0)
    return order, position, unique_order, unique_positions


def sort_key(item):
    try:
        return position_list.index(item)
    except ValueError:
        return len(position_list)


def display_filtered_df(
    df,
    team,
    selected_option1="すべて",
    selected_option2="すべて",
    selected_option3="すべて",
    selected_option4="すべて",
    selected_option5="すべて",
    used_key_num=0,
    order=None,
    position=None,
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
    elif selected_option4 == "直近5試合":
        display_df = display_df.sort_values("game_date", ascending=False).head(5)
    elif selected_option4 == "直近10試合":
        display_df = display_df.sort_values("game_date", ascending=False).head(10)
    else:
        selected_option4 = int(selected_option4.replace("年", "").replace("月", ""))
        if int(selected_option4) > 2000:
            display_df = display_df[display_df["game_date"].dt.year == selected_option4]
        elif int(selected_option4) >= 1 and int(selected_option4) <= 12:
            display_df = display_df[
                display_df["game_date"].dt.month == selected_option4
            ]

    if selected_option5 == "すべて":
        display_df = display_df
    else:
        display_df = display_df[display_df["oppo_team"] == selected_option5]

    if order == "すべて" or order is None:
        display_df = display_df
    else:
        order = order.replace("番", "")
        display_df = display_df[display_df["打順"] == order]

    if position == "すべて" or position is None:
        display_df = display_df
    else:
        display_df = display_df[display_df["守備"] == position]

    return display_df


def display_score_data(score_df, team, used_key_num):
    st.write("## スコアデータ")

    # 計算
    score_df["game_url"] = score_df["game"].apply(get_teams_url, team=team)
    score_df["oppo_team"] = score_df.apply(
        lambda row: get_opponent_team(row, team_dict[team]), axis=1
    )
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

    # フィルタリング
    (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
    ) = display_filter_options(score_df)

    # チーム成績
    # フィルタ後
    _score_df = display_filtered_df(
        score_df,
        team,
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
        used_key_num,
    )
    filtered_score_results = [
        calc_score_data(_score_df, team),
    ]
    filtered_score_results = pd.DataFrame(filtered_score_results)
    filtered_score_results.index = ["フィルタ後"]

    # 期間別
    unique_years = pd.to_datetime(score_df["game_date"]).dt.year.unique()
    unique_months = np.sort(pd.to_datetime(score_df["game_date"]).dt.month.unique())

    score_results = (
        [calc_score_data(display_filtered_df(score_df, team), team)]
        + [
            calc_score_data(
                display_filtered_df(score_df, team, selected_option4=str(year)), team
            )
            for year in unique_years
        ]
        + [
            calc_score_data(
                display_filtered_df(score_df, team, selected_option4=str(month)), team
            )
            for month in unique_months
        ]
    )
    score_results = pd.DataFrame(score_results)
    score_results.index = (
        ["すべて"]
        + [f"{year}年" for year in unique_years]
        + [f"{month}月" for month in unique_months]
    )

    # イニング別
    # フィルタ後
    filtered_inning_score = [
        calc_inning_data(_score_df, type="points", calc="mean"),
        calc_inning_data(_score_df, type="losts", calc="mean"),
    ]
    filtered_inning_score = pd.DataFrame(filtered_inning_score)
    filtered_inning_score.index = ["平均得点", "平均失点"]

    # 期間別得点
    inning_point = (
        [calc_inning_data(score_df, type="points")]
        + [
            calc_inning_data(
                display_filtered_df(score_df, team, selected_option4=str(year)),
                type="points",
            )
            for year in unique_years
        ]
        + [
            calc_inning_data(
                display_filtered_df(score_df, team, selected_option4=str(month)),
                type="points",
            )
            for month in unique_months
        ]
    )
    inning_point = pd.DataFrame(inning_point)
    inning_point.index = (
        ["すべて(得点)"]
        + [f"{year}年(得点)" for year in unique_years]
        + [f"{month}月(得点)" for month in unique_months]
    )

    # 期間別失点
    inning_losts = (
        [calc_inning_data(score_df, type="losts")]
        + [
            calc_inning_data(
                display_filtered_df(score_df, team, selected_option4=str(year)),
                type="losts",
            )
            for year in unique_years
        ]
        + [
            calc_inning_data(
                display_filtered_df(score_df, team, selected_option4=str(month)),
                type="losts",
            )
            for month in unique_months
        ]
    )
    inning_losts = pd.DataFrame(inning_losts)
    inning_losts.index = (
        ["すべて(失点)"]
        + [f"{year}年(失点)" for year in unique_years]
        + [f"{month}月(失点)" for month in unique_months]
    )

    # 表示
    _score_df = _score_df.rename(columns=column_name)
    _score_df["試合日"] = _score_df["試合日"].dt.strftime("%Y/%m/%d")
    st.write("### 試合結果")

    __score_df = _score_df[display_score_columns]
    gb = GridOptionsBuilder.from_dataframe(__score_df)
    gb.configure_default_column(minWidth=50, **{"maxWidth": 150})
    gb.configure_column(
        "詳細",
        header_name="詳細",
        cellRenderer=JsCode(
            """
            class UrlCellRenderer {
                init(params) {
                    this.eGui = document.createElement('a');
                    this.eGui.innerText = "詳細";
                    this.eGui.setAttribute('href', params.value);
                    this.eGui.setAttribute('style', "text-decoration:none");
                    this.eGui.setAttribute('target', "_blank");
                }
                getGui() {
                    return this.eGui;
                }
            }
            """
        ),
    )
    gridOptions = gb.build()
    AgGrid(
        __score_df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
    )
    st.dataframe(filtered_score_results)

    st.write("#### イニング別成績")
    filtered_inning_score = filtered_inning_score.style.background_gradient(
        cmap=cm, axis=1
    )
    filtered_inning_score = filtered_inning_score.format(
        {col: "{:.3f}" for col in filtered_inning_score.columns}
    )
    st.dataframe(filtered_inning_score)

    st.write("### 期間別")
    score_results = score_results.style.background_gradient(cmap=cm, axis=0)
    score_results = score_results.format(score_format)
    st.dataframe(score_results)

    st.write("#### イニング別成績")
    inning_point = inning_point.style.background_gradient(cmap=cm, axis=1)
    inning_point = inning_point.format({col: "{:.3f}" for col in inning_point.columns})
    st.dataframe(inning_point)

    inning_losts = inning_losts.style.background_gradient(cmap=cm, axis=1)
    inning_losts = inning_losts.format({col: "{:.3f}" for col in inning_losts.columns})
    st.dataframe(inning_losts)


def display_batting_data(score_df, batting_df, team, used_key_num):
    # 計算
    score_df["game_url"] = score_df["game"].apply(get_teams_url, team=team)
    score_df["oppo_team"] = score_df.apply(
        lambda row: get_opponent_team(row, team_dict[team]), axis=1
    )
    score_df["game_date"] = pd.to_datetime(score_df["game_date"])
    score_df["result"] = score_df.apply(
        lambda row: win_or_lose(row, team_dict[team]), axis=1
    )

    batting_df["game_date"] = pd.to_datetime(batting_df["game_date"])

    batting_df = pd.merge(
        score_df,
        batting_df,
        on=["game", "game_type", "game_date", "game_day", "game_time"],
    )
    st.write("## 打撃成績")

    # フィルタリング
    (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
    ) = display_filter_options(batting_df)
    (
        regulation,
        order,
        position,
        unique_order,
        unique_position,
    ) = display_filter_batting_all(batting_df)

    # 個人成績
    st.write("### 個人成績")
    players_df = pd.DataFrame()
    for player, group in batting_df.groupby("選手名"):
        if group["打席"].sum() < regulation:
            continue
        _group = display_filtered_df(
            group,
            team,
            selected_option1,
            selected_option2,
            selected_option3,
            selected_option4,
            selected_option5,
            used_key_num=f"{used_key_num}_0",
            order=order,
            position=position,
        )
        try:
            _group = _group.rename(columns=column_name)
            player_df = pd.DataFrame([calc_batting_data(_group)])
            player_df.index = [player]
            player_df["背番号"] = int(player_df["背番号"].values[0])
            players_df = pd.concat([players_df, player_df])
        except ValueError:
            pass
        except IndexError:
            pass
    try:
        # ソート
        players_df = players_df.sort_values("背番号")
    except KeyError:
        pass
    players_df = players_df.style.background_gradient(cmap=cm, axis=0)
    players_df = players_df.format(batting_format)
    st.dataframe(players_df)

    # チーム成績
    st.write("### チーム成績")
    # 期間別
    unique_years = pd.to_datetime(batting_df["game_date"]).dt.year.unique()
    unique_months = np.sort(pd.to_datetime(batting_df["game_date"]).dt.month.unique())
    batting_result = (
        [calc_batting_data(batting_df)]
        + [
            calc_batting_data(
                display_filtered_df(batting_df, team, selected_option4=str(year))
            )
            for year in unique_years
        ]
        + [
            calc_batting_data(
                display_filtered_df(batting_df, team, selected_option4=str(month))
            )
            for month in unique_months
        ]
    )
    batting_result = pd.DataFrame(batting_result)
    batting_result.index = (
        ["すべて"]
        + [f"{year}年" for year in unique_years]
        + [f"{month}月" for month in unique_months]
    )
    st.write("#### 期間別")
    batting_result = batting_result.drop(["背番号", "試合数"], axis=1)
    batting_result = batting_result.style.background_gradient(cmap=cm, axis=0)
    batting_result = batting_result.format(batting_format)
    st.dataframe(batting_result)

    # 打順別
    batting_result_order = [
        calc_batting_data(display_filtered_df(batting_df, team, order=str(order)))
        for order in unique_order
        if order in unique_order
    ]
    batting_result_order = pd.DataFrame(batting_result_order)
    batting_result_order.index = unique_order

    st.write("#### 打順別")
    batting_result_order = batting_result_order.drop(["背番号", "試合数"], axis=1)
    batting_result_order = batting_result_order.style.background_gradient(
        cmap=cm, axis=0
    )
    batting_result_order = batting_result_order.format(batting_format)
    st.dataframe(batting_result_order)

    # 守備別
    batting_result_position = [
        calc_batting_data(display_filtered_df(batting_df, team, position=position))
        for position in position_list
        if position in unique_position
    ]
    batting_result_position = pd.DataFrame(batting_result_position)
    batting_result_position.index = unique_position

    st.write("#### 先発守備位置別")
    batting_result_position = batting_result_position.drop(["背番号", "試合数"], axis=1)
    batting_result_position = batting_result_position.style.background_gradient(
        cmap=cm, axis=0
    )
    batting_result_position = batting_result_position.format(batting_format)
    st.dataframe(batting_result_position)


def display_pitching_data(score_df, pitching_df, team, used_key_num):
    # 計算
    score_df["game_url"] = score_df["game"].apply(get_teams_url, team=team)
    score_df["oppo_team"] = score_df.apply(
        lambda row: get_opponent_team(row, team_dict[team]), axis=1
    )
    score_df["game_date"] = pd.to_datetime(score_df["game_date"])
    score_df["result"] = score_df.apply(
        lambda row: win_or_lose(row, team_dict[team]), axis=1
    )

    pitching_df["game_date"] = pd.to_datetime(pitching_df["game_date"])

    pitching_df = pd.merge(
        score_df,
        pitching_df,
        on=["game", "game_type", "game_date", "game_day", "game_time"],
    )

    st.write("## 投手成績")

    # フィルタリング
    (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
    ) = display_filter_options(pitching_df)

    # 個人成績
    st.write("### 個人成績")
    result_df = pd.DataFrame()
    for player, group in pitching_df.groupby("選手名"):
        _group = display_filtered_df(
            group,
            team,
            selected_option1,
            selected_option2,
            selected_option3,
            selected_option4,
            selected_option5,
            used_key_num=f"{used_key_num}_0",
        )
        try:
            _group = _group.rename(columns=column_name)
            player_df = pd.DataFrame([calc_pitching_data(_group)])
            player_df.index = [player]
            player_df["背番号"] = int(player_df["背番号"].values[0])
            result_df = pd.concat([result_df, player_df])
        except ValueError:
            pass
        except IndexError:
            pass
    try:
        # ソート
        result_df = result_df.sort_values("背番号")
    except KeyError:
        pass
    result_df = result_df.fillna({"勝率": 0, "防御率": 99.99})
    result_df = result_df.style.background_gradient(cmap=cm, axis=0)
    result_df = result_df.format(pitching_format)
    st.dataframe(result_df)

    # チーム成績
    st.write("### チーム成績")
    # 期間別
    unique_years = pd.to_datetime(pitching_df["game_date"]).dt.year.unique()
    unique_months = np.sort(pd.to_datetime(pitching_df["game_date"]).dt.month.unique())
    pitching_result = (
        [calc_pitching_data(pitching_df)]
        + [
            calc_pitching_data(
                display_filtered_df(pitching_df, team, selected_option4=str(year))
            )
            for year in unique_years
        ]
        + [
            calc_pitching_data(
                display_filtered_df(pitching_df, team, selected_option4=str(month))
            )
            for month in unique_months
        ]
    )
    pitching_result = pd.DataFrame(pitching_result)
    pitching_result.index = (
        ["すべて"]
        + [f"{year}年" for year in unique_years]
        + [f"{month}月" for month in unique_months]
    )
    st.write("#### 期間別")
    pitching_result = pitching_result.drop(["背番号", "試合数"], axis=1)
    pitching_result = pitching_result.style.background_gradient(cmap=cm, axis=0)
    pitching_result = pitching_result.format(pitching_format)
    st.dataframe(pitching_result)


def display_player_data(
    score_df, batting_df, pitching_df, team, player_number, player_name, used_key_num
):
    st.write(f"## {player_name} ({player_number})")
    batting_df = batting_df[batting_df["選手名"] == player_name]
    pitching_df = pitching_df[pitching_df["選手名"] == player_name]

    # 計算
    score_df["game_url"] = score_df["game"].apply(get_teams_url, team=team)
    score_df["oppo_team"] = score_df.apply(
        lambda row: get_opponent_team(row, team_dict[team]), axis=1
    )
    score_df["game_date"] = pd.to_datetime(score_df["game_date"])
    score_df["result"] = score_df.apply(
        lambda row: win_or_lose(row, team_dict[team]), axis=1
    )

    batting_df["game_date"] = pd.to_datetime(batting_df["game_date"])
    pitching_df["game_date"] = pd.to_datetime(pitching_df["game_date"])

    batting_df = pd.merge(
        score_df, batting_df, on=["game_type", "game_date", "game_day", "game_time"]
    )
    pitching_df = pd.merge(
        score_df, pitching_df, on=["game_type", "game_date", "game_day", "game_time"]
    )

    # 打撃成績
    # フィルタリング
    (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
    ) = display_filter_options(batting_df)
    order, position, unique_order, unique_position = display_filter_batting(batting_df)

    unique_years = pd.to_datetime(batting_df["game_date"]).dt.year.unique()
    unique_months = np.sort(pd.to_datetime(batting_df["game_date"]).dt.month.unique())
    _batting_df = display_filtered_df(
        batting_df,
        team,
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
        used_key_num=f"{used_key_num}_0",
        order=order,
        position=position,
    )

    try:
        # フィルタ後
        filtered_batting_result = [calc_batting_data(_batting_df)]
        filtered_batting_result = pd.DataFrame(filtered_batting_result)
        filtered_batting_result.index = ["フィルタ後"]

        st.write("### 打撃成績")
        _batting_df = _batting_df.rename(columns=column_name)
        _batting_df["試合日"] = _batting_df["試合日"].dt.strftime("%Y/%m/%d")

        __batting_df = _batting_df[display_batting_columns]
        gb = GridOptionsBuilder.from_dataframe(__batting_df)
        gb.configure_default_column(minWidth=50, **{"maxWidth": 90})
        gb.configure_column(
            "詳細",
            header_name="詳細",
            cellRenderer=JsCode(
                """
                class UrlCellRenderer {
                    init(params) {
                        this.eGui = document.createElement('a');
                        this.eGui.innerText = "詳細";
                        this.eGui.setAttribute('href', params.value);
                        this.eGui.setAttribute('style', "text-decoration:none");
                        this.eGui.setAttribute('target', "_blank");
                    }
                    getGui() {
                        return this.eGui;
                    }
                }
                """
            ),
        )
        gridOptions = gb.build()
        AgGrid(
            __batting_df,
            gridOptions=gridOptions,
            allow_unsafe_jscode=True,
        )
        st.dataframe(filtered_batting_result)
    except IndexError:
        filtered_batting_result = pd.DataFrame(
            index=["フィルタ後"], columns=display_batting_columns
        )
        st.write("#### この条件に合う成績はありません")

    # 期間別
    batting_result = (
        [calc_batting_data(batting_df)]
        + [
            calc_batting_data(
                display_filtered_df(batting_df, team, selected_option4=str(year))
            )
            for year in unique_years
        ]
        + [
            calc_batting_data(
                display_filtered_df(batting_df, team, selected_option4=str(month))
            )
            for month in unique_months
        ]
    )
    batting_result = pd.DataFrame(batting_result)
    batting_result.index = (
        ["すべて"]
        + [f"{year}年" for year in unique_years]
        + [f"{month}月" for month in unique_months]
    )

    st.write("#### 期間別")
    batting_result = batting_result.style.background_gradient(cmap=cm, axis=0)
    batting_result = batting_result.format(batting_format)
    st.dataframe(batting_result)

    # 打順別
    batting_result_order = [
        calc_batting_data(display_filtered_df(batting_df, team, order=str(order)))
        for order in unique_order
        if order in unique_order
    ]
    batting_result_order = pd.DataFrame(batting_result_order)
    batting_result_order.index = unique_order

    st.write("#### 打順別")
    batting_result_order = batting_result_order.style.background_gradient(
        cmap=cm, axis=0
    )
    batting_result_order = batting_result_order.format(batting_format)
    st.dataframe(batting_result_order)

    # 守備別
    batting_result_position = [
        calc_batting_data(display_filtered_df(batting_df, team, position=position))
        for position in position_list
        if position in unique_position
    ]
    batting_result_position = pd.DataFrame(batting_result_position)
    batting_result_position.index = unique_position

    st.write("#### 先発守備位置別")
    batting_result_position = batting_result_position.style.background_gradient(
        cmap=cm, axis=0
    )
    batting_result_position = batting_result_position.format(batting_format)
    st.dataframe(batting_result_position)

    # 投手成績
    st.write("### 投手成績")
    unique_years = pd.to_datetime(pitching_df["game_date"]).dt.year.unique()
    unique_months = np.sort(pd.to_datetime(pitching_df["game_date"]).dt.month.unique())
    _pitching_df = display_filtered_df(
        pitching_df,
        team,
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
        used_key_num=f"{used_key_num}_1",
    )

    try:
        # フィルタ後
        filtered_pitching_result = [calc_pitching_data(_pitching_df)]
        filtered_pitching_result = pd.DataFrame(filtered_pitching_result)
        filtered_pitching_result.index = ["フィルタ後"]

        # 表示
        _pitching_df = _pitching_df.rename(columns=column_name)
        _pitching_df["試合日"] = _pitching_df["試合日"].dt.strftime("%Y/%m/%d")

        __pitching_df = _pitching_df[display_pitching_columns]
        gb = GridOptionsBuilder.from_dataframe(__pitching_df)
        gb.configure_default_column(minWidth=50, **{"maxWidth": 90})
        gb.configure_column(
            "詳細",
            header_name="詳細",
            cellRenderer=JsCode(
                """
                class UrlCellRenderer {
                    init(params) {
                        this.eGui = document.createElement('a');
                        this.eGui.innerText = "詳細";
                        this.eGui.setAttribute('href', params.value);
                        this.eGui.setAttribute('style', "text-decoration:none");
                        this.eGui.setAttribute('target', "_blank");
                    }
                    getGui() {
                        return this.eGui;
                    }
                }
                """
            ),
        )
        gridOptions = gb.build()
        AgGrid(
            __pitching_df,
            gridOptions=gridOptions,
            allow_unsafe_jscode=True,
        )

        st.dataframe(filtered_pitching_result)
    except IndexError:
        filtered_pitching_result = pd.DataFrame(
            index=["フィルタ後"], columns=display_pitching_columns
        )
        st.write("#### この条件に合う成績はありません")

    if pitching_df.shape[0] == 0:
        st.write("#### この選手は投手として登板していません")
    else:
        pitching_result = (
            [
                calc_pitching_data(pitching_df),
            ]
            + [
                calc_pitching_data(
                    display_filtered_df(pitching_df, team, selected_option4=str(year))
                )
                for year in unique_years
            ]
            + [
                calc_pitching_data(
                    display_filtered_df(pitching_df, team, selected_option4=str(month))
                )
                for month in unique_months
            ]
        )
        pitching_result = pd.DataFrame(pitching_result)
        pitching_result.index = (
            ["すべて"]
            + [f"{year}年" for year in unique_years]
            + [f"{month}月" for month in unique_months]
        )

        st.write("#### 期間別")
        pitching_result = pitching_result.fillna({"勝率": 0, "防御率": 99.99})
        pitching_result = pitching_result.style.background_gradient(cmap=cm, axis=0)
        pitching_result = pitching_result.format(pitching_format)
        st.dataframe(pitching_result)
