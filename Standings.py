import streamlit as st
import pandas as pd
import base64
import os

st.set_page_config(page_title="MPL ID Dashboard", layout="wide")

# --- KAMUS LOKASI LOGO LOKAL ---
# Sesuaikan nama file .png/.jpg dengan yang ada di folder 'logos' milikmu
LOGO_MAP = {
    "Onic": "logo/ONIC_Esports.png",
    "Dewa United Esport": "logo/Dewa United Esports.png",
    "Alter Ego": "logo/Alter Ego.png",
    "Team Liquid ID": "logo/Team Liquid.png",
    "EVOS": "logo/EVOS Esports.png",
    "Geek Fam ID": "logo/Geek Fam.png",
    "Bigetron by Vitality": "logo/Bigetron Vitality.png",
    "NAVI": "logo/NAVI.png",
    "RRQ": "logo/RRQ.png"
}

# Fungsi mengubah gambar lokal ke Base64 untuk Tabel
def get_image_base64(img_path):
    if pd.isna(img_path) or not os.path.exists(img_path):
        return None # Mengembalikan kosong jika gambar tidak ditemukan
    with open(img_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
        # Sesuaikan format image/png atau image/jpeg
        return f"data:image/png;base64,{encoded_string}"

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
    
    # Menambahkan kolom Logo lokal yang sudah di-convert
    standings["Logo"] = standings["Team"].map(LOGO_MAP).apply(get_image_base64)
    
    # Susun kolom, Logo di paling depan
    df_standings = standings[["Logo", "Team", "Match Point", "Match W-L", "Net Game Win", "Game W-L"]]

    def highlight_standings(row):
        if row.name <= 2: return ['background-color: rgba(173, 216, 230, 0.2)'] * len(row)
        elif row.name >= 7: return ['background-color: rgba(240, 128, 128, 0.2)'] * len(row)
        else: return [''] * len(row)

    styled_standings = df_standings.style.apply(highlight_standings, axis=1).format({"Net Game Win": "{:+d}"})

    # Tampilkan tabel dengan image column
    st.dataframe(
        styled_standings, 
        use_container_width=True, 
        height=400,
        column_config={
            "Logo": st.column_config.ImageColumn("Logo", width="small") # width="small" memastikan ukuran semua logo rata
        }
    )
    st.markdown("**Keterangan:** 🟦 *Top 2* | ⬜ *Rank 3-6* | 🟥 *Bottom 3*")
