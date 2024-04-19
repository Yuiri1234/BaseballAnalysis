import pandas as pd
import streamlit as st
from display import display_batting_data, display_pitching_data, display_score_data
from info import team_dict


def main():
    team = "ryunen_busters"

    score_df = pd.read_csv(f"data/{team}/score.csv")
    batting_df = pd.read_csv(f"data/{team}/batting.csv")
    pitching_df = pd.read_csv(f"data/{team}/pitching.csv")

    st.title(f"{team_dict[team]} 分析アプリ")
    st.sidebar.title("Menu")
    display_score_data(score_df, team)
    display_batting_data(batting_df)
    display_pitching_data(pitching_df)


if __name__ == "__main__":
    main()
