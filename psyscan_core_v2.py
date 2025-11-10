import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st
from spacy.cli import download as spacy_download
from pathlib import Path

# --- CONFIGURATION ---
# Dossier temporaire inscriptible sur Streamlit Cloud
TMP_MODELS_DIR = Path("/tmp/spacy_models")
TMP_MODELS_DIR.mkdir(exist_ok=True)

# Modèles spaCy + chemins locaux
LANG_MODELS = {
    'fr': ('fr_core_news_sm', TMP_MODELS_DIR / "fr_core_news_sm"),
    'en': ('en_core_web_sm', TMP_MODELS_DIR / "en_core_web_sm")
}

# --- BLOC DE TÉLÉCHARGEMENT DES MODÈLES AU DÉMARRAGE ---
for lang_code, (model_name, model_path) in LANG_MODELS.items():
    if not model_path.exists():
        with st.spinner(f"Téléchargement du modèle spaCy `{model_name}`..."):
            try:
                spacy_download(model_name, False, "--target", str(TMP_MODELS_DIR))
                st.success(f"Modèle `{model_name}` prêt !")
            except Exception as e:
                st.error(f"Échec téléchargement `{model_name}`: {e}")
                raise
    else:
        st.info(f"Modèle `{model_name}` déjà présent.")

# --- FONCTIONS ---
def detect_s1(block, nlp):
    tokens = [t.lemma_.lower() for t in nlp(block) if t.is_alpha and not t.is_stop]
    freq = nltk.FreqDist(tokens)
    return freq.most_common(1)[0][0] if freq else "?"

def classify_regime(s1_history, polarity):
    if len(s1_history) < 2:
        return "?"
    changes = len(set(s1_history[-3:]))
    if changes == 1 and polarity > 0.1:
        return "centripète"
    if changes >= 3 or polarity < -0.1:
        return "centrifuge"
    return "centré (oscillant)"

@st.cache_resource
def load_spacy_model(model_path):
    """Charge un modèle depuis un chemin local (dans /tmp)."""
    return spacy.load(model_path)

def analyze_discourse(text, lang='fr', block_size=5):
    # Détection langue
    try:
        detected = detect(text[:500])
        if detected[:2] != lang[:2]:
            st.warning(f"Langue détectée : **{detected}** ≠ **{lang}** → S1 peut être instable.")
    except:
        pass

    # Sélection du modèle
    model_name, model_path = LANG_MODELS.get(lang[:2], LANG_MODELS['fr'])
    if not model_path.exists():
        st.error(f"Modèle {model_name} non disponible.")
        return [], [], []

    nlp = load_spacy_model(model_path)

    sentences = sent_tokenize(text)
    blocks = [' '.join(sentences[i:i+block_size]) for i in range(0, len(sentences), block_size)]
    s1_history, regimes, key_moments = [], [], []

    for i, block in enumerate(blocks):
        s1 = detect_s1(block, nlp)
        s1_history.append(s1)
        polarity = TextBlob(block).sentiment.polarity
        regime = classify_regime(s1_history, polarity)
        regimes.append(regime)

        if i > 1 and regime != regimes[i-1]:
            key_moments.append({
                "id": i+1, "s1": s1, "regime": regime,
                "quote": block[:150] + "...", "polarity": round(polarity, 2)
            })

    return s1_history, regimes, key_moments
