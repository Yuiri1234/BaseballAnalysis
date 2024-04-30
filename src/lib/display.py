import datetime
import math

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
    batting_metrics,
    column_name,
    display_batting_columns,
    display_pitching_columns,
    display_score_columns,
    low_better_batting,
    low_better_pitching,
    low_better_score,
    pitching_format,
    pitching_metrics,
    position_list,
    score_format,
    team_dict,
)
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

cm1 = sns.color_palette("coolwarm", as_cmap=True)
cm2 = sns.color_palette("coolwarm_r", as_cmap=True)


def calc_inning_points_mean(df):
    return {
        "1回": df["1_points"].mean(),
        "2回": df["2_points"].mean(),
        "3回": df["3_points"].mean(),
        "4回": df["4_points"].mean(),
        "5回": df["5_points"].mean(),
        "6回": df["6_points"].mean(),
        "7回": df["7_points"].mean(),
        "8回": df["8_points"].mean(),
        "9回": df["9_points"].mean(),
    }


def calc_inning_losts_mean(df):
    return {
        "1回": df["1_losts"].mean(),
        "2回": df["2_losts"].mean(),
        "3回": df["3_losts"].mean(),
        "4回": df["4_losts"].mean(),
        "5回": df["5_losts"].mean(),
        "6回": df["6_losts"].mean(),
        "7回": df["7_losts"].mean(),
        "8回": df["8_losts"].mean(),
        "9回": df["9_losts"].mean(),
    }


def calc_win_rate(df):
    if "result" in df.columns:
        win = df[df["result"] == "○"].shape[0]
        lose = df[df["result"] == "☓"].shape[0]
    else:
        win = df[df["結果"] == "○"].shape[0]
        lose = df[df["結果"] == "☓"].shape[0]
    try:
        return win / (win + lose)
    except ZeroDivisionError:
        return 0


def calc_score_data(_scene_df):
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
        on_base_percentage = 0
        slugging_percentage = 0
        average = 0

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

    try:
        babib = (_batting_df["安打"].sum() - _batting_df["本"].sum()) / (
            _batting_df["打数"].sum()
            + _batting_df["犠飛"].sum()
            - _batting_df["三振"].sum()
            - _batting_df["本"].sum()
        )
    except ZeroDivisionError:
        babib = 0

    stolen_bases = _batting_df["盗塁"].sum()
    # 盗塁成功率を計算
    success_rate = (
        ((stolen_bases + 3) / (stolen_bases + 7) - 0.4) * 20 if stolen_bases != 0 else 0
    )
    # 盗塁企図を計算
    try:
        attempt = (
            math.sqrt(stolen_bases / (one_base_hit + _batting_df["四死球"].sum())) / 0.07
            if stolen_bases != 0
            else 0
        )
    except ZeroDivisionError:
        attempt = 0
    # 三塁打割合を計算
    try:
        triples_rate = (
            _batting_df["三塁打"].sum()
            / (
                _batting_df["打数"].sum()
                - _batting_df["本"].sum()
                - _batting_df["三振"].sum()
            )
            / 0.02
            * 10
        )
    except ZeroDivisionError:
        triples_rate = 0
    # 得点割合を計算
    try:
        runs_rate = (
            (_batting_df["得点"].sum() - _batting_df["本"].sum())
            / (
                _batting_df["安打"].sum()
                + _batting_df["四死球"].sum()
                - _batting_df["本"].sum()
            )
            - 0.1
        ) / 0.04
    except ZeroDivisionError:
        runs_rate = 0

    # 各要素が0以下の場合は0に、10以上の場合は10に変換
    attempt = max(0, min(attempt, 10))
    success_rate = max(0, min(success_rate, 10))
    triples_rate = max(0, min(triples_rate, 10))
    runs_rate = max(0, min(runs_rate, 10))

    # Speed Scoreを計算
    speed_score = (attempt + success_rate + triples_rate + runs_rate) / 4

    # SecAを計算
    try:
        seca = (
            total_bases
            - _batting_df["安打"].sum()
            + _batting_df["四死球"].sum()
            + stolen_bases
        ) / _batting_df["打数"].sum()
    except ZeroDivisionError:
        seca = 0

    try:
        if _batting_df.query("守備 != 'DH'").shape[0] == 0:
            error_rate = None
        else:
            error_rate = (
                _batting_df["失策"].sum()
                / _batting_df.query("出場 == '先発' and 守備 != '-' and 守備 != 'DH'").shape[0]
            )
    except ZeroDivisionError:
        error_rate = 0

    if "result" in _batting_df.columns:
        win_num = _batting_df[_batting_df["result"] == "○"].shape[0]
        lose_num = _batting_df[_batting_df["result"] == "☓"].shape[0]
        draw_num = _batting_df[_batting_df["result"] == "△"].shape[0]
    else:
        win_num = _batting_df[_batting_df["結果"] == "○"].shape[0]
        lose_num = _batting_df[_batting_df["結果"] == "☓"].shape[0]
        draw_num = _batting_df[_batting_df["結果"] == "△"].shape[0]

    return {
        "背番号": _batting_df["背番号"].values[0],
        "試合数": _batting_df.shape[0],
        "勝ち": win_num,
        "負け": lose_num,
        "引き分け": draw_num,
        "勝率": calc_win_rate(_batting_df),
        "打率": average,
        "打席": _batting_df["打席"].sum(),
        "打数": _batting_df["打数"].sum(),
        "安打": _batting_df["安打"].sum(),
        "二塁打": _batting_df["二塁打"].sum(),
        "三塁打": _batting_df["三塁打"].sum(),
        "本塁打": _batting_df["本"].sum(),
        "打点": _batting_df["打点"].sum(),
        "得点": _batting_df["得点"].sum(),
        "盗塁": stolen_bases,
        "出塁率": on_base_percentage,
        "塁打数": total_bases,
        "長打率": slugging_percentage,
        "OPS": on_base_percentage + slugging_percentage,
        "IsoP": slugging_percentage - average,  # 純長打率
        "IsoD": on_base_percentage - average,
        "BABIP": babib,
        "wOBA": woba_basic,
        "SecA": seca,
        "三振": _batting_df["三振"].sum(),
        "K%": _batting_df["三振"].sum() / _batting_df["打席"].sum(),
        "四死球": _batting_df["四死球"].sum(),
        "BB%": _batting_df["四死球"].sum() / _batting_df["打席"].sum(),
        "BB/K": bb_k,
        "Spd": speed_score,
        "犠打": _batting_df["犠打"].sum(),
        "犠飛": _batting_df["犠飛"].sum(),
        "併殺打": _batting_df["併殺打"].sum(),
        "敵失": _batting_df["敵失"].sum(),
        "失策": _batting_df["失策"].sum(),
        "失策率": error_rate,
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
        win_rate = 0
    try:
        sum_inning = _pitching_df["投球回(フル)"].sum() + _pitching_df["投球回(1/3)"].sum() / 3
        if sum_inning == 0:
            diffence_rate = 99.999
            whip = 9.999
            k9 = 0
            bb9 = 9.999
            kbb = 0
        else:
            diffence_rate = _pitching_df["自責点"].sum() / sum_inning * 7  # 7回で1試合
            whip = (_pitching_df["被安打"].sum() + _pitching_df["与四死球"].sum()) / sum_inning
            k9 = _pitching_df["奪三振"].sum() / sum_inning * 9
            bb9 = _pitching_df["与四死球"].sum() / sum_inning * 9
            if _pitching_df["与四死球"].sum() == 0:
                if _pitching_df["奪三振"].sum() == 0:
                    kbb = 0
                else:
                    kbb = 9.999
            else:
                kbb = _pitching_df["奪三振"].sum() / _pitching_df["与四死球"].sum()
    except ZeroDivisionError:
        sum_inning = 0
        diffence_rate = 99.999
    sum_inning_str = (
        f"{_pitching_df['投球回(フル)'].sum() + _pitching_df['投球回(1/3)'].sum() // 3}回",
        f"{_pitching_df['投球回(1/3)'].sum() % 3}/3",
    )
    try:
        lob = (
            _pitching_df["被安打"].sum()
            + _pitching_df["与四死球"].sum()
            - _pitching_df["失点"].sum()
        ) / (
            _pitching_df["被安打"].sum()
            + _pitching_df["与四死球"].sum()
            - 1.4 * _pitching_df["被本塁打"].sum()
        )
    except ZeroDivisionError:
        lob = 0
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
        "K/9": k9,
        "与四死球": _pitching_df["与四死球"].sum(),
        "BB/9": bb9,
        "K/BB": kbb,
        "ボーク": _pitching_df["ボーク"].sum(),
        "暴投": _pitching_df["暴投"].sum(),
        "WHIP": whip,
        "LOB%": lob,
    }


def split_inning(inning):
    inning = inning.split("回")
    return pd.Series([int(inning[0]), int(inning[1].split("/")[0])])


def display_filter_options(df, used_key_num=0):
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        options = ["すべて", "公式戦", "練習試合"]
        game_type = st.selectbox("試合種別", options, index=0)
    with col2:
        options = ["すべて", "先攻", "後攻"]
        attack_type = st.selectbox("先攻後攻", options, index=0)
    with col3:
        options = ["すべて", "勝ち", "負け", "引き分け"]
        result_type = st.selectbox("結果", options, index=0)
    with col4:
        options = ["すべて", "以上", "以下"]
        point_diff = st.selectbox("点差", options, index=0)
        if point_diff == "以上":
            point_diff_num = st.number_input(
                "点差(以上)", 0, 100, 5, key=f"score_{used_key_num}_1"
            )
        elif point_diff == "以下":
            point_diff_num = st.number_input(
                "点差(以下)", 0, 100, 3, key=f"score_{used_key_num}_2"
            )
        else:
            point_diff_num = None
    with col5:
        unique_years = pd.to_datetime(df["game_date"]).dt.year.unique()
        unique_months = np.sort(pd.to_datetime(df["game_date"]).dt.month.unique())
        options = (
            ["すべて"]
            + [f"{year}年" for year in unique_years]
            + [f"{month}月" for month in unique_months]
            + ["直近5試合", "直近10試合", "その他"]
        )
        term = st.selectbox("期間", options, index=0)
        if term == "その他":
            term_1, term_2 = display_filter_calendar(df, used_key_num)
        else:
            term_1, term_2 = None, None
    with col6:
        unique_oppo_teams = df["oppo_team"].unique()
        unique_oppo_teams = sorted(unique_oppo_teams)
        options = ["すべて"] + list(unique_oppo_teams)
        oppo_team = st.selectbox("対戦相手", options, index=0)
    with col7:
        unique_game_place = df["game_place"].unique()
        unique_game_place = [
            str(x)
            for x in unique_game_place
            if not (math.isnan(x) if isinstance(x, float) else False) and x != ""
        ]
        unique_game_place = sorted(unique_game_place)
        options = ["すべて"] + list(unique_game_place)
        game_place = st.selectbox("試合場所", options, index=0)

    return {
        "game_type": game_type,
        "attack_type": attack_type,
        "result_type": result_type,
        "point_diff": point_diff,
        "term": term,
        "oppo_team": oppo_team,
        "game_place": game_place,
        "point_diff_num": point_diff_num,
        "term_1": term_1,
        "term_2": term_2,
    }


def display_filter_calendar(df, used_key_num):
    col1, col2 = st.columns(2)
    with col1:
        selected_date1 = st.date_input(
            "期間 (前)",
            datetime.datetime.now() - datetime.timedelta(days=90),
            key=f"calendar_{used_key_num}_1",
        )
    with col2:
        selected_date2 = st.date_input(
            "期間 (後)", datetime.datetime.now(), key=f"calendar_{used_key_num}_2"
        )

    return selected_date1, selected_date2


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
    return regulation, order, position


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
    return order, position


def sort_key(item):
    try:
        return position_list.index(item)
    except ValueError:
        return len(position_list)


def filtering_df(
    df,
    team,
    game_type="すべて",
    attack_type="すべて",
    result_type="すべて",
    point_diff="すべて",
    term="すべて",
    oppo_team="すべて",
    game_place="すべて",
    point_diff_num=None,
    term_1=None,
    term_2=None,
    order=None,
    position=None,
):
    if game_type == "すべて":
        display_df = df
    elif game_type == "公式戦":
        display_df = df[df["game_type"] == "公式戦"]
    elif game_type == "練習試合":
        display_df = df[df["game_type"] == "練習試合"]

    if attack_type == "すべて":
        display_df = display_df
    elif attack_type == "先攻":
        display_df = display_df[display_df["team_name_top"] == team_dict[team]]
    elif attack_type == "後攻":
        display_df = display_df[display_df["team_name_top"] != team_dict[team]]

    if result_type == "すべて":
        display_df = display_df
    elif result_type == "勝ち":
        display_df = display_df[display_df["result"] == "○"]
    elif result_type == "負け":
        display_df = display_df[display_df["result"] == "☓"]
    elif result_type == "引き分け":
        display_df = display_df[display_df["result"] == "△"]

    if point_diff == "すべて":
        display_df = display_df
    elif point_diff == "以上":
        display_df = display_df[display_df["points_diff"].abs() >= point_diff_num]
    elif point_diff == "以下":
        display_df = display_df[display_df["points_diff"].abs() <= point_diff_num]

    if term == "すべて":
        display_df = display_df
    elif term == "その他":
        display_df = filtering_calendar(display_df, term_1, term_2)
    elif term == "直近5試合":
        display_df = display_df.sort_values("game_date", ascending=False).head(5)
    elif term == "直近10試合":
        display_df = display_df.sort_values("game_date", ascending=False).head(10)
    else:
        term = int(term.replace("年", "").replace("月", ""))
        if int(term) > 2000:
            display_df = display_df[display_df["game_date"].dt.year == term]
        elif int(term) >= 1 and int(term) <= 12:
            display_df = display_df[display_df["game_date"].dt.month == term]

    if oppo_team == "すべて":
        display_df = display_df
    else:
        display_df = display_df[display_df["oppo_team"] == oppo_team]

    if game_place == "すべて":
        display_df = display_df
    else:
        display_df = display_df[display_df["game_place"] == game_place]

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


def filtering_calendar(df, selected_date1, selected_date2):
    return df[
        (df["game_date"].dt.date >= selected_date1)
        & (df["game_date"].dt.date <= selected_date2)
    ]


def display_conditional_data(
    df,
    func,
    conditional_type=None,
    team=None,
    unique_years=None,
    unique_months=None,
    unique_order=None,
    unique_positions=None,
):
    if conditional_type == "term":
        # 期間別
        term_results = (
            [func(filtering_df(df, team))]
            + [func(filtering_df(df, team, term=str(year))) for year in unique_years]
            + [func(filtering_df(df, team, term=str(month))) for month in unique_months]
        )
        term_results = pd.DataFrame(term_results)
        term_results.index = (
            ["すべて"]
            + [f"{year}年" for year in unique_years]
            + [f"{month}月" for month in unique_months]
        )
        return term_results
    elif conditional_type == "order":
        # 打順別
        order_results = [
            func(filtering_df(df, team, order=str(order))) for order in unique_order
        ]
        order_results = pd.DataFrame(order_results)
        order_results.index = [i for i in unique_order]
        return order_results
    elif conditional_type == "position":
        # 守備別
        position_results = [
            func(filtering_df(df, team, position=position))
            for position in unique_positions
        ]
        position_results = pd.DataFrame(position_results)
        position_results.index = unique_positions
        return position_results


def display_groupby_player(df, func, type="batting", team=None, selected_options=None):
    st.write("### 個人成績")
    players_df = pd.DataFrame()
    for player, group in df.groupby("選手名"):
        # 通算規定打席数
        if "regulation" in selected_options:
            if group["打席"].sum() < selected_options["regulation"]:
                continue
        if type == "batting":
            _group = filtering_df(
                group,
                team,
                selected_options["game_type"],
                selected_options["attack_type"],
                selected_options["result_type"],
                selected_options["point_diff"],
                selected_options["term"],
                selected_options["oppo_team"],
                selected_options["game_place"],
                selected_options["point_diff_num"],
                selected_options["term_1"],
                selected_options["term_2"],
                selected_options["order"],
                selected_options["position"],
            )
        elif type == "pitching":
            _group = filtering_df(
                group,
                team,
                selected_options["game_type"],
                selected_options["attack_type"],
                selected_options["result_type"],
                selected_options["point_diff"],
                selected_options["term"],
                selected_options["oppo_team"],
                selected_options["game_place"],
                selected_options["point_diff_num"],
                selected_options["term_1"],
                selected_options["term_2"],
            )
        try:
            _group = _group.rename(columns=column_name)
            player_df = pd.DataFrame([func(_group)])
            player_df.index = [player]
            player_df["背番号"] = int(player_df["背番号"].values[0])
            players_df = pd.concat([players_df, player_df])
        except Exception:
            pass
        except IndexError:
            pass
    try:
        # ソート
        players_df = players_df.sort_values("背番号")
    except KeyError:
        players_df = pd.DataFrame(columns=pd.DataFrame([func(df)]).columns)

    if type == "batting":
        display_color_table(players_df, low_better_batting, format_dict=batting_format)
    elif type == "pitching":
        display_color_table(
            players_df,
            low_better_pitching,
            format_dict=pitching_format,
        )


def display_detail_table(df, display_columns):
    df = df.rename(columns=column_name)
    df["試合日"] = df["試合日"].dt.strftime("%Y/%m/%d")

    _df = df[display_columns]
    gb = GridOptionsBuilder.from_dataframe(_df)
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
        _df,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
    )


def display_color_table(df, low_better_list=None, format_dict=None, axis=0, drop=False):
    _df = df.copy()
    if drop:
        _df = _df.drop(["背番号", "試合数"], axis=1)
    _df = _df.style.background_gradient(cmap=cm1, axis=axis)
    if low_better_list == "all":
        _df = _df.background_gradient(cmap=cm2, axis=axis)
    elif low_better_list is not None:
        _df = _df.background_gradient(cmap=cm2, axis=axis, subset=low_better_list)
    if format_dict is not None:
        _df = _df.format(format_dict)
    st.dataframe(_df)


def display_score_data(score_df, team, used_key_num):
    st.write("## スコアデータ")

    # 計算
    score_df[["points", "losts"]] = score_df.apply(
        lambda row: calc_points_losts(row, team_dict[team]),
        axis=1,
        result_type="expand",
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
    selected_options = display_filter_options(score_df, used_key_num)

    # フィルタ後
    _score_df = filtering_df(
        score_df,
        team,
        selected_options["game_type"],
        selected_options["attack_type"],
        selected_options["result_type"],
        selected_options["point_diff"],
        selected_options["term"],
        selected_options["oppo_team"],
        selected_options["game_place"],
        selected_options["point_diff_num"],
        selected_options["term_1"],
        selected_options["term_2"],
    )
    filtered_score_results = [
        calc_score_data(_score_df),
    ]
    filtered_score_results = pd.DataFrame(filtered_score_results)
    filtered_score_results.index = ["フィルタ後"]
    st.write("### 試合結果")
    display_detail_table(_score_df, display_score_columns)
    st.dataframe(filtered_score_results)

    # 期間別
    unique_years = pd.to_datetime(_score_df["game_date"]).dt.year.unique()
    unique_months = np.sort(pd.to_datetime(_score_df["game_date"]).dt.month.unique())
    score_results = display_conditional_data(
        _score_df, calc_score_data, "term", team, unique_years, unique_months
    )
    st.write("#### 期間別")
    display_color_table(
        score_results, low_better_score, format_dict=score_format, axis=0
    )

    # イニング別
    filtered_inning_score = [
        calc_inning_points_mean(_score_df),
        calc_inning_losts_mean(_score_df),
        calc_inning_points_mean(_score_df[_score_df["result"] == "○"]),
        calc_inning_losts_mean(_score_df[_score_df["result"] == "○"]),
        calc_inning_points_mean(_score_df[_score_df["result"] == "☓"]),
        calc_inning_losts_mean(_score_df[_score_df["result"] == "☓"]),
    ]
    filtered_inning_score = pd.DataFrame(filtered_inning_score)
    filtered_inning_score.index = [
        "平均得点",
        "平均失点",
        "平均得点(勝)",
        "平均失点(勝)",
        "平均得点(負)",
        "平均失点(負)",
    ]
    st.write("### イニング別成績")
    filtered_inning_score = filtered_inning_score.T
    display_color_table(
        filtered_inning_score,
        low_better_list=["平均失点", "平均失点(勝)", "平均失点(負)"],
        format_dict={col: "{:.3f}" for col in filtered_inning_score.columns},
        axis=0,
    )

    # 期間別得点
    inning_point = display_conditional_data(
        _score_df, calc_inning_points_mean, "term", team, unique_years, unique_months
    )
    st.write("#### 得点（期間別）")
    display_color_table(
        inning_point,
        low_better_list=None,
        format_dict={col: "{:.3f}" for col in inning_point.columns},
        axis=1,
    )

    # 期間別失点
    inning_losts = display_conditional_data(
        _score_df, calc_inning_losts_mean, "term", team, unique_years, unique_months
    )
    st.write("#### 失点（期間別）")
    display_color_table(
        inning_losts,
        low_better_list="all",
        format_dict={col: "{:.3f}" for col in inning_losts.columns},
        axis=1,
    )


def display_batting_data(score_df, batting_df, team, used_key_num):
    # 計算
    batting_df["game_date"] = pd.to_datetime(batting_df["game_date"])

    batting_df = pd.merge(
        score_df,
        batting_df,
        on=["game", "game_type", "game_date", "game_day", "game_time"],
    )
    st.write("## 打撃成績")

    # フィルタリング
    selected_options = display_filter_options(batting_df, used_key_num)
    (
        regulation,
        order,
        position,
    ) = display_filter_batting_all(batting_df)
    selected_options["regulation"] = regulation
    selected_options["order"] = order
    selected_options["position"] = position

    # 個人成績
    display_groupby_player(
        batting_df, calc_batting_data, "batting", team, selected_options
    )

    # チーム成績
    st.write("### チーム成績")

    _batting_df = filtering_df(
        batting_df,
        team,
        selected_options["game_type"],
        selected_options["attack_type"],
        selected_options["result_type"],
        selected_options["point_diff"],
        selected_options["term"],
        selected_options["oppo_team"],
        selected_options["game_place"],
        selected_options["point_diff_num"],
        selected_options["term_1"],
        selected_options["term_2"],
        selected_options["order"],
        selected_options["position"],
    )

    # 期間別
    st.write("#### 期間別")
    try:
        unique_years = pd.to_datetime(_batting_df["game_date"]).dt.year.unique()
        unique_months = np.sort(
            pd.to_datetime(_batting_df["game_date"]).dt.month.unique()
        )
        batting_result = display_conditional_data(
            _batting_df, calc_batting_data, "term", team, unique_years, unique_months
        )
        batting_result = batting_result.drop(["勝ち", "負け", "引き分け", "勝率"], axis=1)
        display_color_table(
            batting_result,
            low_better_batting,
            format_dict=batting_format,
            axis=0,
            drop=True,
        )
    except IndexError:
        st.write("##### この条件に合う成績はありません")

    # 打順別
    st.write("#### 打順別")
    try:
        unique_order = list(_batting_df["打順"].unique())
        unique_order = [int(i) for i in unique_order if i not in ["-"]]
        unique_order = [i for i in unique_order if i <= 9]
        unique_order = np.sort(unique_order)
        batting_result_order = display_conditional_data(
            _batting_df, calc_batting_data, "order", team, unique_order=unique_order
        )
        batting_result_order = batting_result_order.drop(
            ["勝ち", "負け", "引き分け", "勝率"], axis=1
        )
        display_color_table(
            batting_result_order,
            low_better_batting,
            format_dict=batting_format,
            axis=0,
            drop=True,
        )
    except IndexError:
        st.write("##### この条件に合う成績はありません")
    except KeyError:
        st.write("##### この条件に合う成績はありません")

    # 守備別
    st.write("#### 先発守備位置別")
    try:
        unique_positions = list(_batting_df["守備"].unique())
        unique_positions = [pos for pos in unique_positions if pos not in ["-"]]
        unique_positions = sorted(unique_positions, key=sort_key)
        batting_result_position = display_conditional_data(
            _batting_df,
            calc_batting_data,
            "position",
            team,
            unique_positions=unique_positions,
        )
        batting_result_position = batting_result_position.drop(
            ["勝ち", "負け", "引き分け", "勝率"], axis=1
        )
        display_color_table(
            batting_result_position,
            low_better_batting,
            format_dict=batting_format,
            axis=0,
            drop=True,
        )
    except IndexError:
        st.write("##### この条件に合う成績はありません")
    except KeyError:
        st.write("##### この条件に合う成績はありません")


def display_pitching_data(score_df, pitching_df, team, used_key_num):
    # 計算
    pitching_df["game_date"] = pd.to_datetime(pitching_df["game_date"])

    pitching_df = pd.merge(
        score_df,
        pitching_df,
        on=["game", "game_type", "game_date", "game_day", "game_time"],
    )

    st.write("## 投手成績")

    # フィルタリング
    selected_options = display_filter_options(pitching_df, used_key_num)

    # 個人成績
    display_groupby_player(
        pitching_df, calc_pitching_data, "pitching", team, selected_options
    )

    # チーム成績
    st.write("### チーム成績")

    _pitching_df = filtering_df(
        pitching_df,
        team,
        selected_options["game_type"],
        selected_options["attack_type"],
        selected_options["result_type"],
        selected_options["point_diff"],
        selected_options["term"],
        selected_options["oppo_team"],
        selected_options["game_place"],
        selected_options["point_diff_num"],
        selected_options["term_1"],
        selected_options["term_2"],
    )

    # 期間別
    st.write("#### 期間別")
    try:
        unique_years = pd.to_datetime(_pitching_df["game_date"]).dt.year.unique()
        unique_months = np.sort(
            pd.to_datetime(_pitching_df["game_date"]).dt.month.unique()
        )
        pitching_result = display_conditional_data(
            _pitching_df, calc_pitching_data, "term", team, unique_years, unique_months
        )
        display_color_table(
            pitching_result,
            low_better_pitching,
            format_dict=pitching_format,
            axis=0,
            drop=True,
        )
    except IndexError:
        st.write("##### この条件に合う成績はありません")


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
    score_df["points_diff"] = score_df.apply(
        lambda row: calc_points_diff(row, team_dict[team]), axis=1
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
    selected_options = display_filter_options(batting_df, used_key_num)
    order, position = display_filter_batting(batting_df)

    _batting_df = filtering_df(
        batting_df,
        team,
        selected_options["game_type"],
        selected_options["attack_type"],
        selected_options["result_type"],
        selected_options["point_diff"],
        selected_options["term"],
        selected_options["oppo_team"],
        selected_options["game_place"],
        selected_options["point_diff_num"],
        selected_options["term_1"],
        selected_options["term_2"],
        order=order,
        position=position,
    )

    try:
        # フィルタ後
        filtered_batting_result = [calc_batting_data(_batting_df)]
        filtered_batting_result = pd.DataFrame(filtered_batting_result)
        filtered_batting_result.index = ["フィルタ後"]

        st.write("### 打撃成績")
        display_detail_table(_batting_df, display_batting_columns)
        st.dataframe(filtered_batting_result)
    except IndexError:
        filtered_batting_result = pd.DataFrame(
            index=["フィルタ後"], columns=display_batting_columns
        )
        st.write("##### この条件に合う成績はありません")

    # 期間別
    st.write("#### 期間別")
    try:
        unique_years = pd.to_datetime(_batting_df["game_date"]).dt.year.unique()
        unique_months = np.sort(
            pd.to_datetime(_batting_df["game_date"]).dt.month.unique()
        )
        batting_result = display_conditional_data(
            _batting_df, calc_batting_data, "term", team, unique_years, unique_months
        )
        display_color_table(
            batting_result, low_better_batting, format_dict=batting_format, axis=0
        )
    except IndexError:
        st.write("##### この条件に合う成績はありません")

    # 打順別
    st.write("#### 打順別")
    try:
        unique_order = list(_batting_df["打順"].unique())
        unique_order = [int(i) for i in unique_order if i not in ["-"]]
        unique_order = np.sort(unique_order)
        batting_result_order = display_conditional_data(
            _batting_df, calc_batting_data, "order", team, unique_order=unique_order
        )
        display_color_table(
            batting_result_order, low_better_batting, format_dict=batting_format, axis=0
        )
    except IndexError:
        st.write("##### この条件に合う成績はありません")
    except KeyError:
        st.write("##### この条件に合う成績はありません")

    # 守備別
    st.write("#### 先発守備位置別")
    try:
        unique_positions = list(_batting_df["守備"].unique())
        unique_positions = [pos for pos in unique_positions if pos not in ["-"]]
        unique_positions = sorted(unique_positions, key=sort_key)
        batting_result_position = display_conditional_data(
            _batting_df,
            calc_batting_data,
            "position",
            team,
            unique_positions=unique_positions,
        )
        display_color_table(
            batting_result_position,
            low_better_batting,
            format_dict=batting_format,
            axis=0,
        )
    except IndexError:
        st.write("##### この条件に合う成績はありません")
    except KeyError:
        st.write("##### この条件に合う成績はありません")

    # 投手成績
    st.write("### 投手成績")
    _pitching_df = filtering_df(
        pitching_df,
        team,
        selected_options["game_type"],
        selected_options["attack_type"],
        selected_options["result_type"],
        selected_options["point_diff"],
        selected_options["term"],
        selected_options["oppo_team"],
        selected_options["game_place"],
        selected_options["point_diff_num"],
        selected_options["term_1"],
        selected_options["term_2"],
    )

    try:
        # フィルタ後
        filtered_pitching_result = [calc_pitching_data(_pitching_df)]
        filtered_pitching_result = pd.DataFrame(filtered_pitching_result)
        filtered_pitching_result.index = ["フィルタ後"]

        # 表示
        display_detail_table(_pitching_df, display_pitching_columns)
        st.dataframe(filtered_pitching_result)
    except IndexError:
        filtered_pitching_result = pd.DataFrame(
            index=["フィルタ後"], columns=display_pitching_columns
        )
        st.write("##### この条件に合う成績はありません")

    if pitching_df.shape[0] == 0:
        st.write("#### この選手は投手として登板していません")
    else:
        st.write("#### 期間別")
        try:
            unique_years = pd.to_datetime(_pitching_df["game_date"]).dt.year.unique()
            unique_months = np.sort(
                pd.to_datetime(_pitching_df["game_date"]).dt.month.unique()
            )
            pitching_result = display_conditional_data(
                _pitching_df,
                calc_pitching_data,
                "term",
                team,
                unique_years,
                unique_months,
            )
            display_color_table(
                pitching_result,
                low_better_pitching,
                format_dict=pitching_format,
                axis=0,
            )
        except IndexError:
            st.write("##### この条件に合う成績はありません")


def display_sabermetrics():
    st.write("## セイバーメトリクス")
    st.write("### 打撃")
    for key, value in batting_metrics.items():
        st.write(f"#### {key}")
        if value["説明"] is not None:
            st.write(value["説明"])
        for formula in value["数式"]:
            st.latex(formula)

    st.write("### 投手")
    for key, value in pitching_metrics.items():
        st.write(f"#### {key}")
        if value["説明"] is not None:
            st.write(value["説明"])
        for formula in value["数式"]:
            st.latex(formula)
