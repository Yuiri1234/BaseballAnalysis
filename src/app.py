import os
import pandas as pd

import streamlit as st

def main():
    team = "ryunen_busters"
    
    st.title(f"Baseball Data Analysis App ({team})")
    st.sidebar.title("Menu")
    score_df = pd.read_csv(f"data/{team}/score.csv")
    batting_df = pd.read_csv(f"data/{team}/batting.csv")
    pitching_df = pd.read_csv(f"data/{team}/pitching.csv")

    st.write("## Score Data")
    st.write(score_df)

    st.write("## Batting Data")
    st.write(batting_df)

    st.write("## Pitching Data")
    st.write(pitching_df)

if __name__ == "__main__":
    main()