# psyscan.py
# PSYSCAN v2.5

import streamlit as st
import matplotlib.pyplot as plt
import io
from psyscan_core_v2_5 import analyze_discourse_v25

st.set_page_config(page_title="PSYSCAN v2.5", layout="wide")
st.title("PSYSCAN v2.5 — Sismographe & Poésie du Pouvoir")
st.caption("Indice Ψ stable • Rapport clinique • Visualisation topologique")

st.header("Fondements Épistémologiques")
st.markdown("""
**PSYSCAN révèle la structure du pouvoir — pas les individus.**  
Le **Signifiant-Maître (S1)** est la clé de voûte du discours.  
L'**Indice Ψ** mesure sa force. Le **sismographe** montre son évolution.  
Le **rapport narratif** le traduit en mythe vivant.
""")
st.markdown("---")

col1, _ = st.columns([1, 3])
with col1:
    lang = st.selectbox("Langue", ["Français", "English"])

text = st.text_area("Discours à analyser", height=300, placeholder="Collez ici...")

if st.button("Lancer l’analyse complète", type="primary"):
    if not text.strip():
        st.error("Veuillez saisir un texte.")
    else:
        with st.spinner("Analyse en cours..."):
            result = analyze_discourse_v25(text, lang)

        # === INDICE Ψ ===
        st.subheader("Indice Ψ (stable)")
        col_psi, col_s1 = st.columns(2)
        with col_psi:
            st.metric("**Ψ**", f"{result['psi']:.1f}")
            st.progress(result['psi'] / 100)
        with col_s1:
            st.metric("**S1**", result['s1'].upper())
            st.caption(f"Polarité : {result['polarite']} | je/nous : {result['je']}/{result['nous']} (×{result['ratio_nous_je']:.1f})")

        # === SISMO ===
        st.subheader("Sismographe Symbolique")
        fig, ax = plt.subplots(figsize=(12, 4))
        x = list(range(len(result['regimes'])))
        y = [1 if "centrip" in r else -1 if "centrif" in r else 0 for r in result['regimes']]
        ax.plot(x, y, 'o-', color='red', lw=2.5, markersize=6)
        ax.set_ylim(-1.5, 1.5)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(["Centrifuge", "Oscillant", "Centripète"])
        ax.set_xlabel("Blocs du discours")
        ax.axhline(0, color='gray', linewidth=0.8)
        ax.grid(True, alpha=0.3)
        # Flèche Ψ finale
        ax.annotate(f"Ψ = {result['psi']:.1f}", xy=(len(x)-1, y[-1]), xytext=(10, 20),
                    textcoords='offset points', arrowprops=dict(arrowstyle='->', color='blue'), fontsize=12, color='blue')
        st.pyplot(fig)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        st.download_button("Télécharger sismographe", buf, "psyscan_sismographe.png", "image/png")

        # === RAPPORT NARRATIF ===
        st.subheader("Rapport Clinique du Pouvoir")
        st.markdown(result['rapport'])

        # === EXPORT PDF (simulé) ===
        st.download_button(
            "Exporter en PDF (rapport + image)",
            data=f"PSYSCAN v2.5\n\nS1: {result['s1']}\nΨ: {result['psi']}\n\n{result['rapport']}",
            file_name="psyscan_rapport.txt",
            mime="text/plain"
        )

        st.markdown("---")
        st.markdown("**[Naht Like You Think](https://linktr.ee/iamnaht)** | PSYSCAN v2.5")
