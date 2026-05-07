import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Match Control Center", layout="wide")

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

# --- FUNGSI MENGAMBIL DATA KLASEMEN (UNTUK PLAYOFF) ---
def get_top_6():
    if not os.path.exists("Match.csv"): return []
    df = pd.read_csv("Match.csv", sep=";")
    replacements = {"Bigetron By Vitality": "Bigetron by Vitality"}
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    
    df_played = df.dropna(subset=['Score Home', 'Score Away'])
    teams = {}
    for _, row in df_played.iterrows():
        for t_name in [row['Home Team'], row['Away team']]:
            if t_name not in teams: teams[t_name] = {"Team": t_name, "Match Win": 0, "Match Lose": 0, "Game Win": 0, "Game Lose": 0, "Match Point": 0}
        
        t_a, t_b = teams[row['Home Team']], teams[row['Away team']]
        s_a, s_b = int(row['Score Home']), int(row['Score Away'])
        t_a["Game Win"] += s_a; t_a["Game Lose"] += s_b
        t_b["Game Win"] += s_b; t_b["Game Lose"] += s_a
        if s_a > s_b: t_a["Match Win"] += 1; t_b["Match Lose"] += 1; t_a["Match Point"] += 1
        elif s_b > s_a: t_b["Match Win"] += 1; t_a["Match Lose"] += 1; t_b["Match Point"] += 1

    if not teams: return []
    st_df = pd.DataFrame(list(teams.values()))
    st_df["Net Game Win"] = st_df["Game Win"] - st_df["Game Lose"]
    st_df = st_df.sort_values(by=["Match Point", "Net Game Win"], ascending=[False, False]).reset_index(drop=True)
    return st_df.head(6)['Team'].tolist()

def load_data():
    df = pd.read_csv("Match.csv", sep=";")
    replacements = {"Bigetron By Vitality": "Bigetron by Vitality"}
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    return df

st.markdown("<h1 style='text-align: center;'>🎛️ MATCH CONTROL CENTER</h1>", unsafe_allow_html=True)

# ==========================================
# PEMISAH HALAMAN (RADIO BUTTON)
# ==========================================
st.markdown("---")
mode = st.radio(
    "Pilih Fase Turnamen:",
    ["📅 Regular Season", "🔥 Playoff"],
    horizontal=True
)
st.markdown("---")

# ==========================================
# BAGIAN 1: REGULAR SEASON
# ==========================================
if mode == "📅 Regular Season":
    df_main = load_data()
    weeks = df_main['Week'].unique()
    
    # Tambahkan expander agar tampilan lebih rapi dan tidak terlalu panjang ke bawah
    for week in weeks:
        with st.expander(f"### {week}", expanded=True):
            matches_in_week = df_main[df_main['Week'] == week]
            cols = st.columns(3)
            
            for i, (idx, match) in enumerate(matches_in_week.iterrows()):
                col_idx = i % 3
                with cols[col_idx]:
                    with st.container(border=True):
                        val_h = int(match['Score Home']) if pd.notnull(match['Score Home']) else 0
                        val_a = int(match['Score Away']) if pd.notnull(match['Score Away']) else 0
                        
                        st.markdown(f"<div style='text-align: center; color: gray; font-size: 12px;'>Match {i+1}</div>", unsafe_allow_html=True)
                        
                        path_h = LOGO_MAP.get(match['Home Team'])
                        path_a = LOGO_MAP.get(match['Away team'])
                        
                        c_logo_h, c_text_h, c_vs, c_text_a, c_logo_a = st.columns([1, 2, 1, 2, 1])
                        
                        with c_logo_h:
                            if path_h and os.path.exists(path_h): st.image(path_h, width=45)
                        
                        with c_text_h:
                            st.markdown(f"<div style='font-size:13px; font-weight:bold; white-space:nowrap;'>{match['Home Team']}</div>", unsafe_allow_html=True)
                            score_h = st.number_input("Score", min_value=0, max_value=2, value=val_h, key=f"rs_h_{idx}", label_visibility="collapsed")
                        
                        with c_vs:
                            st.markdown("<div style='text-align: center; font-weight: bold; margin-top: 25px;'>VS</div>", unsafe_allow_html=True)
                        
                        with c_text_a:
                            st.markdown(f"<div style='font-size:13px; font-weight:bold; white-space:nowrap; text-align:right;'>{match['Away team']}</div>", unsafe_allow_html=True)
                            score_a = st.number_input("Score", min_value=0, max_value=2, value=val_a, key=f"rs_a_{idx}", label_visibility="collapsed")
                        
                        with c_logo_a:
                            if path_a and os.path.exists(path_a): st.image(path_a, width=45)
                        
                        if st.button("💾 Simpan Update", key=f"btn_rs_{idx}", use_container_width=True):
                            df_main.at[idx, 'Score Home'] = score_h
                            df_main.at[idx, 'Score Away'] = score_a
                            df_main.to_csv("Match.csv", index=False, sep=";")
                            st.success("Skor tersimpan!")
                            st.rerun()

# ==========================================
# BAGIAN 2: PLAYOFF
# ==========================================
elif mode == "🔥 Playoff":
    st.subheader("Update Skor Playoff (BO5 & BO7)")
    
    top_6 = get_top_6()
    
    if len(top_6) < 6:
        st.warning("Belum ada 6 tim di klasemen. Selesaikan pertandingan Regular Season terlebih dahulu.")
    elif not os.path.exists("Match Playoff.csv"):
        st.error("File 'Match Playoff.csv' tidak ditemukan di folder.")
    else:
        df_po = pd.read_csv("Match Playoff.csv", sep=";")
        r1, r2, r3, r4, r5, r6 = top_6[0], top_6[1], top_6[2], top_6[3], top_6[4], top_6[5]

        # Logika Kalkulasi Pemenang/Kalah Berantai
        teams_in_match = {}
        
        def set_match_data(idx, t_home, t_away):
            teams_in_match[idx] = {"Home": t_home, "Away": t_away}
            s_h = df_po.at[idx, 'Score Home'] if pd.notna(df_po.at[idx, 'Score Home']) else 0
            s_a = df_po.at[idx, 'Score Away'] if pd.notna(df_po.at[idx, 'Score Away']) else 0
            
            winner, loser = f"Winner M{idx+1}", f"Loser M{idx+1}"
            if s_h > s_a: winner, loser = t_home, t_away
            elif s_a > s_h: winner, loser = t_away, t_home
            return winner, loser

        # Menghitung alur turnamen dari M1 sampai M8
        w1, l1 = set_match_data(0, r3, r6)           # M1: Rank 3 vs Rank 6
        w2, l2 = set_match_data(1, r4, r5)           # M2: Rank 4 vs Rank 5
        w3, l3 = set_match_data(2, r2, w1)           # M3: Rank 2 vs Winner M1
        w4, l4 = set_match_data(3, r1, w2)           # M4: Rank 1 vs Winner M2
        w5, l5 = set_match_data(4, l3, l4)           # M5: Loser M3 vs Loser M4
        w6, l6 = set_match_data(5, w3, w4)           # M6: Winner M3 vs Winner M4
        w7, l7 = set_match_data(6, w5, l6)           # M7: Winner M5 vs Loser M6
        w8, l8 = set_match_data(7, w6, w7)           # M8: Winner M6 vs Winner M7

        # Tampilkan Grid Playoff (2 Kolom agar lebih lebar)
        cols_po = st.columns(2)
        
        for i, row in df_po.iterrows():
            with cols_po[i % 2]:
                with st.container(border=True):
                    team_h = teams_in_match[i]["Home"]
                    team_a = teams_in_match[i]["Away"]
                    
                    val_h = int(row['Score Home']) if pd.notna(row['Score Home']) else 0
                    val_a = int(row['Score Away']) if pd.notna(row['Score Away']) else 0
                    
                    st.markdown(f"<div style='text-align: center; color: gray; font-size: 12px;'>{row['Match']}</div>", unsafe_allow_html=True)
                    
                    path_h = LOGO_MAP.get(team_h)
                    path_a = LOGO_MAP.get(team_a)
                    
                    c_logo_h, c_text_h, c_vs, c_text_a, c_logo_a = st.columns([1, 2, 1, 2, 1])
                    
                    with c_logo_h:
                        if path_h and os.path.exists(path_h): st.image(path_h, width=45)
                    
                    with c_text_h:
                        st.markdown(f"<div style='font-size:13px; font-weight:bold; white-space:nowrap;'>{team_h}</div>", unsafe_allow_html=True)
                        max_score = 4 if i == 7 else 3 # M8 (Grand Final) Max 4, sisanya Max 3
                        score_h = st.number_input("Score", min_value=0, max_value=max_score, value=val_h, key=f"po_h_{i}", label_visibility="collapsed")
                    
                    with c_vs:
                        st.markdown("<div style='text-align: center; font-weight: bold; margin-top: 25px;'>VS</div>", unsafe_allow_html=True)
                    
                    with c_text_a:
                        st.markdown(f"<div style='font-size:13px; font-weight:bold; white-space:nowrap; text-align:right;'>{team_a}</div>", unsafe_allow_html=True)
                        score_a = st.number_input("Score", min_value=0, max_value=max_score, value=val_a, key=f"po_a_{i}", label_visibility="collapsed")
                    
                    with c_logo_a:
                        if path_a and os.path.exists(path_a): st.image(path_a, width=45)
                    
                    if st.button("💾 Simpan Skor Playoff", key=f"btn_po_{i}", use_container_width=True):
                        df_po.at[i, 'Score Home'] = score_h
                        df_po.at[i, 'Score Away'] = score_a
                        df_po.to_csv("Match Playoff.csv", index=False, sep=";")
                        st.success(f"Skor {row['Match']} tersimpan!")
                        st.rerun()
