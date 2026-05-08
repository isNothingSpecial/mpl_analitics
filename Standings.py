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
# --- TAB 2: BAGAN PLAYOFF LENGKAP ---
with tab_playoff:
    st.subheader("Bagan Playoff (Double Elimination)")
    
    if len(df_standings) < 6:
        st.warning("Menunggu data klasemen minimal 6 tim untuk menyusun bagan playoff.")
    elif not os.path.exists("Match Playoff.csv"):
        st.warning("Menunggu file data Playoff dibuat di Match Controller.")
    else:
        # 1. Ambil Top 6 Tim dari Klasemen
        top_6 = df_standings.head(6)['Team'].tolist()
        r1, r2, r3, r4, r5, r6 = top_6[0], top_6[1], top_6[2], top_6[3], top_6[4], top_6[5]

        # 2. Baca file skor Playoff
        df_po = pd.read_csv("Match Playoff.csv", sep=";")

        # 3. Fungsi untuk mengekstrak tim, skor, pemenang, dan yang kalah
        def get_match_info(idx, t_home, t_away):
            s_h = df_po.at[idx, 'Score Home'] if pd.notna(df_po.at[idx, 'Score Home']) else 0
            s_a = df_po.at[idx, 'Score Away'] if pd.notna(df_po.at[idx, 'Score Away']) else 0
            
            # Tentukan pemenang dan yang kalah sementara
            winner, loser = f"Winner M{idx+1}", f"Loser M{idx+1}"
            if s_h > s_a: 
                winner, loser = t_home, t_away
            elif s_a > s_h: 
                winner, loser = t_away, t_home
                
            return t_home, int(s_h), t_away, int(s_a), winner, loser

        # 4. Kalkulasi Alur Turnamen (M1 sampai M8)
        h1, sh1, a1, sa1, w1, l1 = get_match_info(0, r3, r6)
        h2, sh2, a2, sa2, w2, l2 = get_match_info(1, r4, r5)
        h3, sh3, a3, sa3, w3, l3 = get_match_info(2, r2, w1)
        h4, sh4, a4, sa4, w4, l4 = get_match_info(3, r1, w2)
        h5, sh5, a5, sa5, w5, l5 = get_match_info(4, l3, l4)
        h6, sh6, a6, sa6, w6, l6 = get_match_info(5, w3, w4)
        h7, sh7, a7, sa7, w7, l7 = get_match_info(6, w5, l6)
        h8, sh8, a8, sa8, w8, l8 = get_match_info(7, w6, w7)

        # 5. Desain Bagan (4 Kolom)
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown("#### Babak 1 (Play-Ins)")
            with st.container(border=True):
                st.markdown("**Match 1**")
                st.write(f"{h1} : **{sh1}**")
                st.write(f"{a1} : **{sa1}**")
            
            with st.container(border=True):
                st.markdown("**Match 2**")
                st.write(f"{h2} : **{sh2}**")
                st.write(f"{a2} : **{sa2}**")

        with c2:
            st.markdown("#### Babak 2")
            with st.container(border=True):
                st.markdown("**Match 3 (Upper Semi)**")
                st.write(f"{h3} : **{sh3}**")
                st.write(f"{a3} : **{sa3}**")
            
            with st.container(border=True):
                st.markdown("**Match 4 (Upper Semi)**")
                st.write(f"{h4} : **{sh4}**")
                st.write(f"{a4} : **{sa4}**")
                
            st.markdown("---")
            with st.container(border=True):
                st.markdown("**Match 5 (Lower Semi)**")
                st.write(f"{h5} : **{sh5}**")
                st.write(f"{a5} : **{sa5}**")

        with c3:
            st.markdown("#### Babak 3 (Finals)")
            with st.container(border=True):
                st.markdown("**Match 6 (Upper Final)**")
                st.write(f"{h6} : **{sh6}**")
                st.write(f"{a6} : **{sa6}**")
                
            st.markdown("---")
            with st.container(border=True):
                st.markdown("**Match 7 (Lower Final)**")
                st.write(f"{h7} : **{sh7}**")
                st.write(f"{a7} : **{sa7}**")

        with c4:
            st.markdown("#### Babak 4")
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("<h4 style='text-align:center; color:gold;'>Grand Final (M8)</h4>", unsafe_allow_html=True)
                st.write(f"🏆 {h8} : **{sh8}**")
                st.write(f"🏆 {a8} : **{sa8}**")
                
    st.info("💡 Bagan ini otomatis membaca hasil dari halaman Match Control Center.")
