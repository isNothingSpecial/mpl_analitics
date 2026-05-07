import streamlit as st
import pandas as pd
import base64
import os

# 1. Konfigurasi Halaman
st.set_page_config(page_title="MPL ID Standings & Playoff", layout="wide")

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

# --- FUNGSI HELPER ---
def get_image_base64(img_path):
    """Mengonversi gambar lokal ke Base64 agar muncul di tabel klasemen."""
    if not img_path or not os.path.exists(img_path):
        return None
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return f"data:image/png;base64,{base64.b64encode(data).decode()}"
    except:
        return None

def load_data():
    """Membaca CSV dan membersihkan duplikasi nama tim."""
    if not os.path.exists("Match.csv"):
        # Jika file tidak ada, buat cangkang kosong
        df = pd.DataFrame(columns=['Week', 'Home Team', 'Score Home', 'Score Away', 'Away team'])
        df.to_csv("Match.csv", index=False, sep=";")
        return df
    
    df = pd.read_csv("Match.csv", sep=";")
    # Pembersihan nama tim (Menangani kasus 'by' dan 'By' pada Bigetron)
    replacements = {
        "Bigetron By Vitality": "Bigetron by Vitality",
        "Bigetron By Vitality ": "Bigetron by Vitality"
    }
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    return df

# --- PROSES DATA ---
df_main = load_data()

# Fungsi hitung klasemen (hanya yang sudah ada skornya)
def get_standings(df):
    df_played = df.dropna(subset=['Score Home', 'Score Away'])
    teams = {}
    
    for _, row in df_played.iterrows():
        for t_name in [row['Home Team'], row['Away team']]:
            if t_name not in teams:
                teams[t_name] = {"Team": t_name, "Match Win": 0, "Match Lose": 0, "Game Win": 0, "Game Lose": 0, "Match Point": 0}
        
        t_a, t_b = teams[row['Home Team']], teams[row['Away team']]
        s_a, s_b = int(row['Score Home']), int(row['Score Away'])
        
        t_a["Game Win"] += s_a; t_a["Game Lose"] += s_b
        t_b["Game Win"] += s_b; t_b["Game Lose"] += s_a
        
        if s_a > s_b:
            t_a["Match Win"] += 1; t_b["Match Lose"] += 1; t_a["Match Point"] += 1
        elif s_b > s_a:
            t_b["Match Win"] += 1; t_a["Match Lose"] += 1; t_b["Match Point"] += 1

    if not teams:
        return pd.DataFrame()
        
    st_df = pd.DataFrame(list(teams.values()))
    st_df["Match W-L"] = st_df["Match Win"].astype(str) + " - " + st_df["Match Lose"].astype(str)
    st_df["Net Game Win"] = st_df["Game Win"] - st_df["Game Lose"]
    st_df["Game W-L"] = st_df["Game Win"].astype(str) + " - " + st_df["Game Lose"].astype(str)
    st_df = st_df.sort_values(by=["Match Point", "Net Game Win"], ascending=[False, False]).reset_index(drop=True)
    st_df.index += 1
    return st_df

df_standings = get_standings(df_main)

# --- TAMPILAN UI ---
st.markdown("<h1 style='text-align: center;'>🏆 MPL ID SEASON ANALYTICS</h1>", unsafe_allow_html=True)

# GABUNGKAN DALAM TABS
tab_std, tab_update, tab_playoff = st.tabs(["📊 Klasemen", "🎛️ Update Center", "🔥 Bagan Playoff"])

# --- TAB 1: KLASEMEN ---
with tab_std:
    if df_standings.empty:
        st.info("Belum ada data pertandingan yang dimainkan.")
    else:
        df_view = df_standings.copy()
        df_view["Logo"] = df_view["Team"].map(LOGO_MAP).apply(get_image_base64)
        
        # Susun kolom
        cols_to_show = ["Logo", "Team", "Match Point", "Match W-L", "Net Game Win", "Game W-L"]
        
        def style_rows(row):
            if row.name <= 2: return ['background-color: rgba(173, 216, 230, 0.1)'] * len(row)
            if row.name >= 7: return ['background-color: rgba(240, 128, 128, 0.1)'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df_view[cols_to_show].style.apply(style_rows, axis=1).format({"Net Game Win": "{:+d}"}),
            use_container_width=True, height=450,
            column_config={"Logo": st.column_config.ImageColumn("Logo", width="small")}
        )
        st.caption("🟦 Upper Bracket | ⬜ Playoff | 🟥 Tereliminasi")

# --- TAB 2: UPDATE CENTER (GRID 3 KOLOM) ---
with tab_update:
    st.subheader("Update Skor Regular Season")
    all_weeks = df_main['Week'].unique()
    
    for week in all_weeks:
        with st.expander(f"📅 {week}", expanded=(week == all_weeks[0])):
            m_in_week = df_main[df_main['Week'] == week]
            grid_cols = st.columns(3)
            
            for i, (idx, match) in enumerate(m_in_week.iterrows()):
                with grid_cols[i % 3]:
                    with st.container(border=True):
                        # Layout Card
                        c_l, c_v, c_r = st.columns([2, 1, 2])
                        
                        # Data Skor (Default 0 jika NaN)
                        s_h = int(match['Score Home']) if pd.notnull(match['Score Home']) else 0
                        s_a = int(match['Score Away']) if pd.notnull(match['Score Away']) else 0
                        
                        with c_l:
                            st.image(LOGO_MAP.get(match['Home Team'], ""), width=40)
                            st.caption(match['Home Team'])
                            new_h = st.number_input("Skor", 0, 2, s_h, key=f"h_{idx}", label_visibility="collapsed")
                        with c_v:
                            st.markdown("<h4 style='text-align:center; margin-top:25px;'>VS</h4>", unsafe_allow_html=True)
                        with c_r:
                            st.image(LOGO_MAP.get(match['Away team'], ""), width=40)
                            st.caption(match['Away team'])
                            new_a = st.number_input("Skor", 0, 2, s_a, key=f"a_{idx}", label_visibility="collapsed")
                        
                        if st.button("Simpan", key=f"btn_{idx}", use_container_width=True):
                            df_main.at[idx, 'Score Home'] = new_h
                            df_main.at[idx, 'Score Away'] = new_a
                            df_main.to_csv("Match.csv", index=False, sep=";")
                            st.toast("Data tersimpan!")
                            st.rerun()

# --- TAB 3: PLAYOFF BRACKET ---
with tab_playoff:
    if len(df_standings) < 6:
        st.warning("Butuh minimal 6 tim di klasemen untuk menyusun bagan playoff.")
    else:
        top_6 = df_standings.head(6)['Team'].tolist()
        r1, r2, r3, r4, r5, r6 = top_6[0], top_6[1], top_6[2], top_6[3], top_6[4], top_6[5]
        
        st.markdown("### 🏆 Playoff Bracket (Auto-Generated)")
        p_col1, p_col2, p_col3 = st.columns(3)
        
        with p_col1:
            st.markdown("**[Play-ins]**")
            with st.container(border=True):
                st.write(f"Match 1: **{r3}** vs **{r6}**")
            with st.container(border=True):
                st.write(f"Match 2: **{r4}** vs **{r5}**")
        
        with p_col2:
            st.markdown("**[Upper Semis]**")
            with st.container(border=True):
                st.write(f"**{r2}** vs Winner M1")
            with st.container(border=True):
                st.write(f"**{r1}** vs Winner M2")
        
        with p_col3:
            st.markdown("**[Next Stage]**")
            st.write("Upper Final & Lower Bracket Stage")
            st.image("https://raw.githubusercontent.com/username/repo/main/playoff_ref.png", width=300) # Ganti URL atau hapus
