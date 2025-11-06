import streamlit as st
from psyscan_core_v2 import analyze_discourse
import matplotlib.pyplot as plt
import io

# === CONFIG ===
st.set_page_config(page_title="PSYSCAN v2.1", layout="wide")
st.title("PSYSCAN v2.1 — Sismographe du Discours")
st.caption("*Analyse lacanienne en temps réel : évolution symbolique, topologie, points de rupture.*")

# === ZONE 1 : LANGUE ===
col1, _ = st.columns([1, 3])
with col1:
    lang = st.selectbox("Langue du discours", ["Français", "English"], help="Choix explicite pour stabilité du S1")

# === ZONE 2 : DISCOURS + PARAMÈTRES ===
text = st.text_area(
    "Colle ton discours ici",
    height=300,
    placeholder="Ex. : Appel du 18 juin 1940..."
)
block_size = st.slider("Taille des blocs (phrases)", 1, 15, 5, help="Plus petit = plus sensible")

# === LANCEMENT ===
if st.button("Lancer le sismographe", type="primary"):
    if not text.strip():
        st.error("Veuillez coller un discours.")
    else:
        with st.spinner("Analyse en cours..."):
            s1_history, regimes, key_moments = analyze_discourse(text, lang, block_size)

        # === SISMO VISUEL (ANIMÉ SIMULÉ) ===
        st.subheader("Sismographe Symbolique")
        fig, ax = plt.subplots(figsize=(12, 5))
        x = list(range(len(regimes)))
        y = [1 if r.startswith("centrip") else -1 if "centrif" in r else 0 for r in regimes]
        ax.plot(x, y, 'o-', color='red', lw=2.5, markersize=6)
        ax.set_ylim(-1.5, 1.5)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(["Centrifuge", "Oscillant", "Centripète"])
        ax.set_xlabel("Blocs du discours")
        ax.set_title("Évolution topologique du discours")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        # === EXPORT PNG ===
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        st.download_button("Télécharger le sismographe", buf.getvalue(), "sismographe.png", "image/png")

        # === RÉTROSPECTIVE : POINTS CLÉS ===
        st.subheader("Points clés du tremblement symbolique")
        for m in key_moments:
            with st.expander(f"Bloc {m['id']} — **{m['s1']}** → **{m['regime']}** (Polarité: {m['polarity']})"):
                st.write(m['quote'])

        # === ANALYSE GÉNÉRALE DIDACTIQUE ===
        st.subheader("Analyse globale")
        s1_global = max(set(s1_history), key=s1_history.count)
        regime_final = regimes[-1]
        st.write(f"""
        - **Signifiant maître (S1)** : **{s1_global}** → ancre le récit symbolique.  
        - **Régime final** : **{regime_final}** → structure dominante à la fin.  
        - **Évolution interne** : Le discours passe par **{len(key_moments)} ruptures majeures**, révélant une dynamique de **contrôle → oscillation → {regime_final}**.  
        - **Interprétation** : Le pouvoir se configure autour de **{s1_global}** comme acte symbolique. Les ruptures marquent les moments où le contrat social est renégocié.
        """)

        # === LIEN PÉDAGOGIQUE ===
        st.markdown("---")
        st.markdown("**PSYSCAN v2.1** — Outil d’analyse lacanienne du discours | [GitHub](https://github.com/nahtlikeyouthink/psyscan/tree/v2.1-sismographe) | Licence éthique héritée")
