import streamlit as st

st.set_page_config(page_title = "Pycycle")

header = st.container()

with header:
    st.title("Construction des modèles")
    st.markdown("### Contexte du projet")
    st.markdown('### Jeu de données initial')
    st.markdown('### Sélection des compteurs')
    st.markdown('### Enrichissement des données')
    st.markdown('### Traitement des données')
    st.markdown('### Perspectives')