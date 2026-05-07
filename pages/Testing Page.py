import streamlit as st
import pandas as pd
import base64
import os

st.set_page_config(page_title="MPL ID Dashboard", layout="wide")

# --- KAMUS LOKASI LOGO LOKAL ---
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

def get_image_base64(img_path):
    if pd.isna(img_path) or not os.path.exists(img_path):
        return None
    with open(img_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"

def load_data():
    if not os.path.exists("Match.csv"):
        return pd.DataFrame(columns=['Week', 'Home Team', 'Score Home', 'Score Away', 'Away team'])
    df = pd.read_csv("Match.csv", sep=";")
    replacements = {"Bigetron By Vitality": "Bigetron by Vitality"}
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    return df

df_main = load_data()

st.markdown("<h1 style='text-align: center;'>🏆 MPL INDONESIA ANALYTICS</h1>", unsafe_allow_html=True)
st.markdown("---")

# PROSES DATA KLASEMEN
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

df_standings = pd.DataFrame()
if teams:
    standings = pd.DataFrame(list(teams.values()))
    standings["Match W-L"] = standings["Match Win"].astype(str) + " - " + standings["Match Lose"].astype(str)
    standings["Net Game Win"] = standings["Game Win"] - standings["Game Lose"]
    standings["Game W-L"] = standings["Game Win"].astype(str) + " - " + standings["Game Lose"].astype(str)
    df_standings = standings.sort_values(by=["Match Point", "Net Game Win"], ascending=[False, False]).reset_index(drop=True)
    df_standings.index = df_standings.index + 1

# ==========================================
# UI MENGGUNAKAN TABS
# ==========================================
tab_standings, tab_playoff = st.tabs(["📊 Regular Season Standings", "🔥 Detail Bagan Playoff"])

# --- TAB 1: KLASEMEN REGULAR SEASON ---
with tab_standings:
    if df_standings.empty:
        st.info("Belum ada pertandingan yang diselesaikan.")
    else:
        df_standings["Logo"] = df_standings["Team"].map(LOGO_MAP).apply(get_image_base64)
        df_display = df_standings[["Logo", "Team", "Match Point", "Match W-L", "Net Game Win", "Game W-L"]]

        def highlight_standings(row):
            if row.name <= 2: return ['background-color: rgba(173, 216, 230, 0.2)'] * len(row)
            elif row.name >= 7: return ['background-color: rgba(240, 128, 128, 0.2)'] * len(row)
            else: return [''] * len(row)

        styled_standings = df_display.style.apply(highlight_standings, axis=1).format({"Net Game Win": "{:+d}"})

        st.dataframe(
            styled_standings, 
            use_container_width=True, height=400,
            column_config={"Logo": st.column_config.ImageColumn("Logo", width="small")}
        )
        st.markdown("**Keterangan:** 🟦 *Top 2: Upper Bracket* | ⬜ *Rank 3-6: Play-In* | 🟥 *Bottom 3: Not Qualified*")

# --- TAB 2: BAGAN PLAYOFF LENGKAP ---
with tab_playoff:
    st.subheader("Bagan Playoff (Double Elimination)")
    
    if len(df_standings) < 6:
        st.warning("Menunggu data klasemen minimal 6 tim untuk menyusun bagan playoff.")
    else:
        # Ambil Top 6 Tim
        top_6 = df_standings.head(6)['Team'].tolist()
        r1, r2, r3, r4, r5, r6 = top_6[0], top_6[1], top_6[2], top_6[3], top_6[4], top_6[5]

        # Desain Bagan (4 Kolom untuk menunjukkan flow dari kiri ke kanan)
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown("#### Babak 1 (Play-Ins)")
            st.caption("Loser Eliminated")
            with st.container(border=True):
                st.write("**Match 1 (M1)**")
                st.write(f"🔹 {r3} (R3)")
                st.write(f"🔹 {r6} (R6)")
            
            with st.container(border=True):
                st.write("**Match 2 (M2)**")
                st.write(f"🔹 {r4} (R4)")
                st.write(f"🔹 {r5} (R5)")

        with c2:
            st.markdown("#### Babak 2")
            st.caption("Upper Semifinals")
            with st.container(border=True):
                st.write("**Match 3 (M3)**")
                st.write(f"🔹 {r2} (R2)")
                st.write(f"🔹 Winner M1")
            
            with st.container(border=True):
                st.write("**Match 4 (M4)**")
                st.write(f"🔹 {r1} (R1)")
                st.write(f"🔹 Winner M2")
                
            st.markdown("---")
            st.caption("Lower Semifinal")
            with st.container(border=True):
                st.write("**Match 5 (M5)**")
                st.write(f"🔻 Loser M3")
                st.write(f"🔻 Loser M4")

        with c3:
            st.markdown("#### Babak 3 (Finals)")
            st.caption("Upper Bracket Final")
            with st.container(border=True):
                st.write("**Match 6 (M6)**")
                st.write(f"⭐ Winner M3")
                st.write(f"⭐ Winner M4")
                
            st.markdown("---")
            st.caption("Lower Bracket Final")
            with st.container(border=True):
                st.write("**Match 7 (M7)**")
                st.write(f"🔥 Winner M5")
                st.write(f"🔻 Loser M6")

        with c4:
            st.markdown("#### Babak 4")
            st.caption("Grand Final (BO7)")
            # Padding untuk menurunkan kotak ke tengah
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("<h4 style='text-align:center; color:gold;'>Match 8 (M8)</h4>", unsafe_allow_html=True)
                st.write(f"🏆 Winner M6 (Upper)")
                st.write(f"🏆 Winner M7 (Lower)")
                
    st.info("💡 Bagan ini akan terus ter-update secara otomatis menyesuaikan peringkat 1 hingga 6 di akhir Regular Season.")
