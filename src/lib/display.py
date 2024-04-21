import datetime

import pandas as pd
import seaborn as sns
import streamlit as st
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from lib.calculate import (
    calc_inning_losts,
    calc_inning_points,
    calc_points_diff,
    calc_points_losts,
    win_or_lose,
    get_teams_url,
    get_opponent_team,
)
from lib.info import batting_format, column_name, pitching_format, score_format, team_dict

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

    return {
        "試合数": _batting_df.shape[0],
        "打率": average,
        "打席": _batting_df["打席"].sum(),
        "打数": _batting_df["打数"].sum(),
        "安打": _batting_df["安打"].sum(),
        "本塁打": _batting_df["本"].sum(),
        "打点": _batting_df["打点"].sum(),
        "得点": _batting_df["得点"].sum(),
        "盗塁": _batting_df["盗塁"].sum(),
        "出塁率": on_base_percentage,
        "長打率": slugging_percentage,
        "OPS": on_base_percentage + slugging_percentage,
        "二塁打": _batting_df["二塁打"].sum(),
        "三塁打": _batting_df["三塁打"].sum(),
        "塁打数": total_bases,
        "三振": _batting_df["三振"].sum(),
        "四死球": _batting_df["四死球"].sum(),
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
        diffence_rate = _pitching_df["自責点"].sum() / sum_inning * 7  # 7回で1試合
    except ZeroDivisionError:
        sum_inning = 0
        diffence_rate = None
    sum_inning_str = (
        f"{_pitching_df['投球回(フル)'].sum() + _pitching_df['投球回(1/3)'].sum() // 3}回",
        f"{_pitching_df['投球回(1/3)'].sum() % 3}/3",
    )
    return {
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
        options = ["すべて"] + [f"{year}年" for year in unique_years] + ["直近5試合", "その他"]
        selected_option4 = st.selectbox("年", options, index=0)
    with col5:
        unique_oppo_teams = df["oppo_team"].unique()
        options = ["すべて"] + list(unique_oppo_teams)
        selected_option5 = st.selectbox("対戦相手", options, index=0)
    return selected_option1, selected_option2, selected_option3, selected_option4, selected_option5


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
    selected_option1="すべて",
    selected_option2="すべて",
    selected_option3="すべて",
    selected_option4="すべて",
    selected_option5="すべて",
    used_key_num=0,
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
    else:
        year = int(selected_option4.replace("年", ""))
        display_df = display_df[display_df["game_date"].dt.year == year]

    if selected_option5 == "すべて":
        display_df = display_df
    else:
        display_df = display_df[display_df["oppo_team"] == selected_option5]
    return display_df


def display_score_data(score_df, team, used_key_num):
    st.write("## 試合結果")

    # 計算
    score_df["game_url"] = score_df["game"].apply(get_teams_url, team=team)
    score_df["oppo_team"] = score_df.apply(lambda row: get_opponent_team(row, team_dict[team]), axis=1)
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

    # 年度別
    unique_years = pd.to_datetime(score_df["game_date"]).dt.year.unique()
    score_results = [calc_score_data(display_filtered_df(score_df, team), team)] + [
        calc_score_data(
            display_filtered_df(score_df, team, selected_option4=str(year)), team
        )
        for year in unique_years
    ]
    score_results = pd.DataFrame(score_results)
    score_results.index = ["すべて"] + [f"{year}年" for year in unique_years]

    # イニング別
    # フィルタ後
    filtered_inning_score = [
        calc_inning_data(_score_df, type="points", calc="mean"),
        calc_inning_data(_score_df, type="losts", calc="mean"),
    ]
    filtered_inning_score = pd.DataFrame(filtered_inning_score)
    filtered_inning_score.index = ["平均得点", "平均失点"]

    # 年度別得点
    inning_point = [calc_inning_data(score_df, type="points")] + [
        calc_inning_data(
            display_filtered_df(score_df, team, selected_option4=str(year)),
            type="points",
        )
        for year in unique_years
    ]
    inning_point = pd.DataFrame(inning_point)
    inning_point.index = ["すべて(得点)"] + [f"{year}年(得点)" for year in unique_years]

    # 年度別失点
    inning_losts = [calc_inning_data(score_df, type="losts")] + [
        calc_inning_data(
            display_filtered_df(score_df, team, selected_option4=str(year)),
            type="losts",
        )
        for year in unique_years
    ]
    inning_losts = pd.DataFrame(inning_losts)
    inning_losts.index = ["すべて(失点)"] + [f"{year}年(失点)" for year in unique_years]

    # 表示
    _score_df = _score_df.rename(columns=column_name)
    _score_df["試合日"] = _score_df["試合日"].dt.strftime("%Y/%m/%d")
    st.write("### チーム成績")

    __score_df = _score_df[
        [
            "詳細",
            "試合種別",
            "試合日",
            "曜日",
            "対戦相手",
            "先攻",
            "後攻",
            "得点",
            "失点",
            "得失点差",
            "結果",
        ]
    ]
    gb = GridOptionsBuilder.from_dataframe(__score_df)
    gb.configure_default_column(
        minWidth=50,
        **{"maxWidth": 150}
    )
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
        )
    )
    gridOptions = gb.build()
    AgGrid(
        __score_df, 
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        
    )
    st.dataframe(filtered_score_results)

    score_results = score_results.style.background_gradient(cmap=cm, axis=0)
    score_results = score_results.format(score_format)
    st.dataframe(score_results)

    st.write("### イニング別成績")
    st.write("#### フィルタ後")
    filtered_inning_score = filtered_inning_score.style.background_gradient(
        cmap=cm, axis=1
    )
    filtered_inning_score = filtered_inning_score.format(
        {col: "{:.3f}" for col in filtered_inning_score.columns}
    )
    st.dataframe(filtered_inning_score)

    st.write("#### 年度別")
    inning_point = inning_point.style.background_gradient(cmap=cm, axis=1)
    inning_point = inning_point.format({col: "{:.3f}" for col in inning_point.columns})
    st.dataframe(inning_point)

    inning_losts = inning_losts.style.background_gradient(cmap=cm, axis=1)
    inning_losts = inning_losts.format({col: "{:.3f}" for col in inning_losts.columns})
    st.dataframe(inning_losts)


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

    # 計算
    score_df["game_url"] = score_df["game"].apply(get_teams_url, team=team)
    score_df["oppo_team"] = score_df.apply(lambda row: get_opponent_team(row, team_dict[team]), axis=1)
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

    # フィルタリング
    (
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
    ) = display_filter_options(batting_df)

    batting_df = batting_df[batting_df["選手名"] == player_name]
    unique_years = pd.to_datetime(batting_df["game_date"]).dt.year.unique()
    _batting_df = display_filtered_df(
        batting_df,
        team,
        selected_option1,
        selected_option2,
        selected_option3,
        selected_option4,
        selected_option5,
        used_key_num=f"{used_key_num}_0",
    )

    filtered_batting_result = [calc_batting_data(_batting_df)]
    filtered_batting_result = pd.DataFrame(filtered_batting_result)
    filtered_batting_result.index = ["フィルタ後"]

    batting_result = [calc_batting_data(batting_df)] + [
        calc_batting_data(
            display_filtered_df(batting_df, team, selected_option4=str(year))
        )
        for year in unique_years
    ]
    batting_result = pd.DataFrame(batting_result)
    batting_result.index = ["すべて"] + [f"{year}年" for year in unique_years]

    # 表示
    st.write("### 打撃成績")
    _batting_df = _batting_df.rename(columns=column_name)
    _batting_df["試合日"] = _batting_df["試合日"].dt.strftime("%Y/%m/%d")

    __batting_df =_batting_df[
        [
            "詳細",
            "選手名",
            "試合種別",
            "試合日",
            "対戦相手",
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
    gb = GridOptionsBuilder.from_dataframe(__batting_df)
    gb.configure_default_column(
        minWidth=50,
        **{"maxWidth": 90}
    )
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
        )
    )
    gridOptions = gb.build()
    AgGrid(
        __batting_df, 
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
    )
    st.dataframe(filtered_batting_result)

    if batting_result.shape[0] == 1:
        st.write("#### この選手は打者として出場していません")
    else:
        batting_result = batting_result.style.background_gradient(cmap=cm, axis=0)
        batting_result = batting_result.format(batting_format)
        st.dataframe(batting_result)

    st.write("### 投手成績")
    pitching_df = pitching_df[pitching_df["選手名"] == player_name]
    unique_years = pd.to_datetime(pitching_df["game_date"]).dt.year.unique()
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

    filtered_pitching_result = [calc_pitching_data(_pitching_df)]
    filtered_pitching_result = pd.DataFrame(filtered_pitching_result)
    filtered_pitching_result.index = ["フィルタ後"]

    pitching_result = [calc_pitching_data(pitching_df),] + [
        calc_pitching_data(
            display_filtered_df(pitching_df, team, selected_option4=str(year))
        )
        for year in unique_years
    ]
    pitching_result = pd.DataFrame(pitching_result)
    pitching_result.index = ["すべて"] + [f"{year}年" for year in unique_years]

    # 表示
    _pitching_df = _pitching_df.rename(columns=column_name)
    _pitching_df["試合日"] = _pitching_df["試合日"].dt.strftime("%Y/%m/%d")

    __pitching_df = _pitching_df[
        [
            "詳細",
            "選手名",
            "試合種別",
            "試合日",
            "対戦相手",
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
    gb = GridOptionsBuilder.from_dataframe(__pitching_df)
    gb.configure_default_column(
        minWidth=50,
        **{"maxWidth": 90}
    )
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
        )
    )
    gridOptions = gb.build()
    AgGrid(
        __pitching_df, 
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
    )

    st.dataframe(filtered_pitching_result)

    if pitching_result.shape[0] == 1:
        st.write("#### この選手は投手として登板していません")
    else:
        pitching_result = pitching_result.style.background_gradient(cmap=cm, axis=0)
        pitching_result = pitching_result.format(pitching_format)
        st.write(pitching_result)
