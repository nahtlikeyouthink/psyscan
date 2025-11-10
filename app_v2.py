# psyscan.py
# PSYSCAN v2.1 – Scanner méta-psychique du discours public
# Licence : AGPL-3.0 + ETHICAL_GUIDELINES.md
# Auteur : NAHT LIKE YOU THINK – DOI : https://doi.org/10.5281/zenodo.17504541

import streamlit as st
from psyscan_core_v2 import analyze_discourse
import matplotlib.pyplot as plt
import io

# === CONFIG ===
st.set_page_config(page_title="PSYSCAN v2.1", layout="wide")

# === TITRE ===
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
            try:
                s1_history, regimes, key_moments, psi = analyze_discourse(text, lang, block_size)
            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {str(e)}")
                st.stop()

        # === INDICE Ψ ===
        st.subheader("Indice Ψ — Force du Signifiant-Maître")
        col_psi, col_help = st.columns([1, 4])
        with col_psi:
            st.metric(
        label="**Indice Ψ**",
        value=f"{psi:.3f}",
        help="Centralité du S1 (0 = dispersé, 1 = dominant)"
        )
        with col_help:
            st.caption("Plus Ψ est élevé, plus le discours dépend d’un seul signifiant. Ex : 0.85 = S1 ultra-dominant.")

        st.markdown("---")

                # === JAUGE VISUELLE ===
        st.progress(psi)
        if psi > 0.7:
            st.warning("**Ψ élevé** → Risque de totalisation symbolique (S1 hégémonique)")
        elif psi < 0.3:
            st.info("**Ψ bas** → Discours dispersé, peu d’ancrage symbolique")
        else:
            st.success("**Ψ équilibré** → Discours structuré mais souple")
            
        # === SISMO VISUEL ===
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
        plt.close(fig)

        # === EXPORT PNG ===
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        st.download_button("Télécharger le sismographe", buf, "sismographe.png", "image/png")

        # === RÉTROSPECTIVE ===
        st.subheader("Points clés du tremblement symbolique")
        if key_moments:
            for m in key_moments:
                with st.expander(f"Bloc {m['id']} — **{m['s1']}** → **{m['regime']}** (Polarité: {m['polarity']})"):
                    st.write(m['quote'])
        else:
            st.info("Aucun point de rupture détecté.")

        # === ANALYSE GÉNÉRALE ===
        st.subheader("Analyse globale")
        if s1_history:
            s1_global = max(set(s1_history), key=s1_history.count)
            regime_final = regimes[-1]
            st.write(f"""
            - **Signifiant maître (S1)** : **{s1_global}** → ancre le récit symbolique.
            - **Régime final** : **{regime_final}** → structure dominante.
            - **Ruptures** : **{len(key_moments)}** moments de bascule.
            - **Interprétation** : Le discours organise le pouvoir autour de **{s1_global}**, avec des oscillations révélant les points de renégociation du lien social.
            """)

        # =========================================================
        # PRÉSENTATION
        # =========================================================
        st.markdown("---")
        st.header("Fondements Épistémologiques")
        st.markdown("""
        **PSYSCAN révèle la structure du pouvoir — pas les individus.**  
        Cet outil open-source part d'une prémisse psychanalytique et philosophique : le discours politique est d'abord **pulsionnel** et **structurant**. Le **Signifiant-Maître (S1)** n'est pas un choix conscient, mais la *clé de voûte* autour de laquelle le pouvoir s'organise. PSYSCAN agit comme un **sismographe du discours**, mesurant les **tremblements structurels** pour révéler la nature et la stabilité du pouvoir.
        """)
        st.subheader("Mesurer l'Invisible (L'Indice Ψ)")
        st.markdown("""
        L'**Indice $\Psi$ (Psi)** quantifie la **centralité** du S1 dans le discours.  
        Un score élevé indique une **dépendance critique** à un seul signifiant — un point de fragilité ou de totalisation symbolique.
        """)
        # === LIEN PÉDAGOGIQUE ===
        st.markdown("---")
        st.markdown("**PSYSCAN v2.1** — Outil d’analyse | [GitHub](https://github.com/nahtlikeyouthink/psyscan/tree/v2.1-sismographe) | Sismographe du Discours")

# LIEN CLIQUABLE GARANTI
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; margin-top: 20px; font-size: 0.9em; color: #666;">
        <a href="https://linktr.ee/iamnaht" target="_blank" style="color: #666; text-decoration: underline;">
            Naht Like You Think
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
