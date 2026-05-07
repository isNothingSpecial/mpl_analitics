# File: app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MPL Standings", layout="wide")

def load_data():
    df = pd.read_csv("Match.csv", sep=";")
    replacements = {"Bigetron By Vitality": "Bigetron by Vitality"}
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    return df

df_main = load_data()

st.markdown("<h1 style='text-align: center;'>🏆 MPL INDONESIA STANDINGS</h1>", unsafe_allow_html=True)
st.markdown("---")

df_played = df_main.dropna(subset=['Score Home', 'Score Away'])
teams = {}
def get_or_create_team(team_name):
    if team_name not in teams:
        teams[team_name] = {"Team": team_name, "Match Win": 0, "Match Lose": 0, "Game Win": 0, "Game Lose": 0, "Match Point": 0}
    return teams[team_name]

for _, row in df_played.iterrows():
    t_a, t_b = get_or_create_team(row['Home Team']), get_or_create_team(row['Away team'])
    score_a, score_b = int(row['Score Home']), int(row['Score Away'])
    
    t_a["Game Win"] += score_a; t_a["Game Lose"] += score_b
    t_b["Game Win"] += score_b; t_b["Game Lose"] += score_a
    
    if score_a > score_b:
        t_a["Match Win"] += 1; t_b["Match Lose"] += 1; t_a["Match Point"] += 1
    elif score_b > score_a:
        t_b["Match Win"] += 1; t_a["Match Lose"] += 1; t_b["Match Point"] += 1

if not teams:
    st.info("Belum ada pertandingan yang diselesaikan.")
else:
    standings = pd.DataFrame(list(teams.values()))
    standings["Match W-L"] = standings["Match Win"].astype(str) + " - " + standings["Match Lose"].astype(str)
    standings["Net Game Win"] = standings["Game Win"] - standings["Game Lose"]
    standings["Game W-L"] = standings["Game Win"].astype(str) + " - " + standings["Game Lose"].astype(str)
    standings = standings.sort_values(by=["Match Point", "Net Game Win"], ascending=[False, False]).reset_index(drop=True)
    standings.index = standings.index + 1
    
    df_standings = standings[["Team", "Match Point", "Match W-L", "Net Game Win", "Game W-L"]]

    def highlight_standings(row):
        if row.name <= 2: return ['background-color: rgba(173, 216, 230, 0.2)'] * len(row)
        elif row.name >= 7: return ['background-color: rgba(240, 128, 128, 0.2)'] * len(row)
        else: return [''] * len(row)

    styled_standings = df_standings.style.apply(highlight_standings, axis=1).format({"Net Game Win": "{:+d}"})

    st.dataframe(styled_standings, use_container_width=True, height=400)
    st.markdown("**Keterangan:** 🟦 *Top 2 (Playoff Upper Bracket)* | ⬜ *Rank 3-6 (Playoff via Play-In)* | 🟥 *Bottom 3 (Not Qualified)*")
