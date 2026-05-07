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
    if not os.path.exists("Match.csv"):
        return pd.DataFrame(columns=['Week', 'Home Team', 'Score Home', 'Score Away', 'Away team'])
    df = pd.read_csv("Match.csv", sep=";")
    replacements = {"Bigetron By Vitality": "Bigetron by Vitality"}
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    return df

# --- PROSES DATA KLASEMEN ---
df_main = load_data()
df_played = df_main.dropna(subset=['Score Home', 'Score Away'])

teams = {}
def get_or_create_team(name):
    if name not in teams:
        teams[name] = {"Team": name, "Match Win": 0, "Match Lose": 0, "Game Win": 0, "Game Lose": 0, "Match Point": 0}
    return teams[name]

for _, row in df_played.iterrows():
    t_a, t_b = get_or_create_team(row['Home Team']), get_or_create_team(row['Away team'])
    s_a, s_b = int(row['Score Home']), int(row['Score Away'])
    t_a["Game Win"] += s_a; t_a["Game Lose"] += s_b
    t_b["Game Win"] += s_b; t_b["Game Lose"] += s_a
    if s_a > s_b:
        t_a["Match Win"] += 1; t_b["Match Lose"] += 1; t_a["Match Point"] += 1
    elif s_b > s_a:
        t_b["Match Win"] += 1; t_a["Match Lose"] += 1; t_b["Match Point"] += 1

# Menghasilkan DataFrame Klasemen
if not teams:
    df_standings = pd.DataFrame()
else:
    standings = pd.DataFrame(list(teams.values()))
    standings["Match W-L"] = standings["Match Win"].astype(str) + " - " + standings["Match Lose"].astype(str)
    standings["Net Game Win"] = standings["Game Win"] - standings["Game Lose"]
    standings["Game W-L"] = standings["Game Win"].astype(str) + " - " + standings["Game Lose"].astype(str)
    standings = standings.sort_values(by=["Match Point", "Net Game Win"], ascending=[False, False]).reset_index(drop=True)
    standings.index = standings.index + 1
    df_standings = standings

# ==========================================
# UI UTAMA DENGAN TABS
# ==========================================
st.markdown("<h1 style='text-align: center;'>🏆 MPL ID SEASON ANALYTICS</h1>", unsafe_allow_html=True)

tab_standings, tab_playoff = st.tabs(["📊 Regular Season Standings", "🔥 Playoff Bracket"])

# --- TAB 1: STANDINGS ---
with tab_standings:
    if df_standings.empty:
        st.warning("Belum ada data pertandingan.")
    else:
        # Tambahkan logo ke df untuk ditampilkan
        df_display = df_standings.copy()
        df_display["Logo"] = df_display["Team"].map(LOGO_MAP).apply(get_image_base64)
        
        final_df = df_display[["Logo", "Team", "Match Point", "Match W-L", "Net Game Win", "Game W-L"]]
        
        def highlight(row):
            if row.name <= 2: return ['background-color: rgba(173, 216, 230, 0.15)'] * len(row)
            elif row.name >= 7: return ['background-color: rgba(240, 128, 128, 0.15)'] * len(row)
            return [''] * len(row)

        st.dataframe(
            final_df.style.apply(highlight, axis=1).format({"Net Game Win": "{:+d}"}),
            use_container_width=True,
            height=450,
            column_config={"Logo": st.column_config.ImageColumn("Logo", width="small")}
        )
        st.info("💡 Rank 1-2: Upper Bracket Semifinals | Rank 3-6: Play-ins | Rank 7-9: Not Qualified")

# --- TAB 2: PLAYOFF BRACKET ---
with tab_playoff:
    if len(df_standings) < 6:
        st.warning("Klasemen belum mencapai 6 tim. Bagan Playoff otomatis muncul setelah 6 tim terdaftar.")
    else:
        # Ambil Top 6
        top_6 = df_standings.head(6)['Team'].tolist()
        r1, r2, r3, r4, r5, r6 = top_6[0], top_6[1], top_6[2], top_6[3], top_6[4], top_6[5]

        st.markdown("### Bagan Mekanisme Playoff")
        
        # Grid layout untuk simulasi Bracket
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown("#### [1] Play-ins")
            # Card Match 1
            with st.container(border=True):
                st.write(f"**{r3}** (Rank 3)")
                st.write(f"**{r6}** (Rank 6)")
                st.caption("Pemenang vs Rank 2")
            
            # Card Match 2
            with st.container(border=True):
                st.write(f"**{r4}** (Rank 4)")
                st.write(f"**{r5}** (Rank 5)")
                st.caption("Pemenang vs Rank 1")

        with c2:
            st.markdown("#### [2] Upper Semifinals")
            with st.container(border=True):
                st.write(f"**{r2}** (Rank 2)")
                st.write("🆚 Winner Match 1")
            
            with st.container(border=True):
                st.write(f"**{r1}** (Rank 1)")
                st.write("🆚 Winner Match 2")

        with c3:
            st.markdown("#### [3] Lower & Final Stage")
            st.markdown("""
            - Tim yang kalah di **Upper Semi** turun ke **Lower Bracket**.
            - Tim yang kalah di **Play-ins** langsung tereliminasi.
            - Format: **BO5** (Semifinals) & **BO7** (Grand Final).
            """)
