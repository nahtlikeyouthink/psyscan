# psyscan_v25.py
import streamlit as st
from psyscan_core_v2_5 import analyze_discourse_v25

st.set_page_config(page_title="PSYSCAN v2.5.2", layout="wide")
st.title("PSYSCAN v2.5.2 — Clinique du Pouvoir")

text = st.text_area("Colle ton discours ici :", height=300)
lang = st.selectbox("Langue :", ["Français", "English"])

if st.button("Analyser"):
    if text.strip():
        with st.spinner("Analyse en cours..."):
            result = analyze_discourse_v25(text, lang)
        st.success(f"Ψ: {result['psi']}")
        st.markdown(f"**S1:** {result['s1'].upper()} | **Centralité:** {int(result['centralite']*100)} % | **Polarité:** {result['polarite']}")
        st.markdown(result['rapport'])
    else:
        st.error("Veuillez entrer un texte.")
