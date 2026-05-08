import streamlit as st
st.write ("Hanya Halaman Testing,makanya isinya random")
import plotly.graph_objects as go

st.subheader("Radar Chart: Head-to-Head Stats")

# 1. Tentukan kategori statistik yang ingin dibandingkan
categories = ['KDA', 'Gold/Min', 'Objective', 'Teamfight', 'Turret Push']

# 2. Buat kanvas grafik
fig = go.Figure()

# 3. Masukkan data Tim 1 (Misal: ONIC)
fig.add_trace(go.Scatterpolar(
      r=[8.5, 9.0, 8.0, 9.5, 7.5], # Nilai/Skor untuk masing-masing kategori
      theta=categories,
      fill='toself',
      name='ONIC',
      line_color='yellow'
))

# 4. Masukkan data Tim 2 (Misal: RRQ)
fig.add_trace(go.Scatterpolar(
      r=[7.5, 8.5, 9.5, 8.0, 9.0], 
      theta=categories,
      fill='toself',
      name='RRQ',
      line_color='orange'
))

# 5. Percantik tampilan layout
fig.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, 10] # Skala nilai 0 sampai 10
    )),
  showlegend=True,
  margin=dict(l=40, r=40, t=40, b=40)
)

# 6. Tampilkan di Streamlit!
st.plotly_chart(fig, use_container_width=True)
