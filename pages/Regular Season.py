import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Update Match", layout="wide")

# --- KAMUS LOKASI LOGO LOKAL ---
LOGO_MAP = {
    "Onic": "logos/onic.png",
    "Dewa United Esport": "logos/dewa.png",
    "Alter Ego": "logos/alterego.png",
    "Team Liquid ID": "logos/liquid.png",
    "EVOS": "logos/evos.png",
    "Geek Fam ID": "logos/geekfam.png",
    "Bigetron by Vitality": "logos/btr.png",
    "NAVI": "logos/navi.png",
    "RRQ": "logos/rrq.png"
}

def load_data():
    df = pd.read_csv("Match.csv", sep=";")
    replacements = {"Bigetron By Vitality": "Bigetron by Vitality"}
    df['Home Team'] = df['Home Team'].str.strip().replace(replacements)
    df['Away team'] = df['Away team'].str.strip().replace(replacements)
    return df

df_main = load_data()

st.markdown("<h1 style='text-align: center;'>🎛️ MATCH CONTROL CENTER</h1>", unsafe_allow_html=True)
st.markdown("---")

weeks = df_main['Week'].unique()

for week in weeks:
    st.markdown(f"### {week}")
    matches_in_week = df_main[df_main['Week'] == week]
    cols = st.columns(3)
    
    for i, (idx, match) in enumerate(matches_in_week.iterrows()):
        col_idx = i % 3
        with cols[col_idx]:
            with st.container(border=True):
                val_h = int(match['Score Home']) if pd.notnull(match['Score Home']) else None
                val_a = int(match['Score Away']) if pd.notnull(match['Score Away']) else None
                
                st.markdown(f"<div style='text-align: center; color: gray; font-size: 12px;'>Match {i+1}</div>", unsafe_allow_html=True)
                
                # Mengambil jalur path logo
                path_h = LOGO_MAP.get(match['Home Team'])
                path_a = LOGO_MAP.get(match['Away team'])
                
                # Membagi menjadi 5 kolom (logo - input - VS - input - logo)
                c_logo_h, c_text_h, c_vs, c_text_a, c_logo_a = st.columns([1, 2, 1, 2, 1])
                
                with c_logo_h:
                    if path_h and os.path.exists(path_h):
                        st.image(path_h, width=45) # Ukuran fix 45 pixel
                
                with c_text_h:
                    st.markdown(f"<div style='font-size:13px; font-weight:bold; white-space:nowrap;'>{match['Home Team']}</div>", unsafe_allow_html=True)
                    score_h = st.number_input("Score", min_value=0, max_value=2, value=val_h, key=f"h_{idx}", label_visibility="collapsed")
                
                with c_vs:
                    st.markdown("<div style='text-align: center; font-weight: bold; margin-top: 25px;'>VS</div>", unsafe_allow_html=True)
                
                with c_text_a:
                    st.markdown(f"<div style='font-size:13px; font-weight:bold; white-space:nowrap; text-align:right;'>{match['Away team']}</div>", unsafe_allow_html=True)
                    score_a = st.number_input("Score", min_value=0, max_value=2, value=val_a, key=f"a_{idx}", label_visibility="collapsed")
                
                with c_logo_a:
                    if path_a and os.path.exists(path_a):
                        st.image(path_a, width=45) # Ukuran fix 45 pixel
                
                if st.button("💾 Simpan Update", key=f"btn_{idx}", use_container_width=True):
                    df_main.at[idx, 'Score Home'] = score_h
                    df_main.at[idx, 'Score Away'] = score_a
                    df_main.to_csv("Match.csv", index=False, sep=";")
                    
                    st.success("Skor tersimpan!")
                    st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
