# psyscan_core_v2.py
import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st

# --- NLTK : Téléchargement forcé des ressources ---
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)  # Crucial pour NLTK 3.9+
    nltk.download('stopwords', quiet=True)
except Exception as e:
    st.error(f"Erreur NLTK : {e}")
    st.stop()

# --- MODÈLES SPAcy ---
LANG_MODELS = {
    'fr': 'fr_core_news_sm',
    'en': 'en_core_web_sm'
}

@st.cache_resource
def load_spacy_model(model_name):
    try:
        return spacy.load(model_name)
    except Exception as e:
        st.error(f"Modèle spaCy `{model_name}` introuvable : {e}")
        st.stop()

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

def analyze_discourse(text, lang='Français', block_size=5):
    # Map lang to code
    lang_code = 'fr' if lang == 'Français' else 'en'

    # Détection langue
    try:
        detected = detect(text[:500])
        if detected != lang_code:
            st.warning(f"Langue détectée : **{detected}** ≠ **{lang_code}**")
    except:
        pass

    # Modèle spaCy
    model_name = LANG_MODELS.get(lang_code, LANG_MODELS['fr'])
    nlp = load_spacy_model(model_name)

    # Découpage phrases (avec fallback)
    try:
        sentences = sent_tokenize(text, language=lang_code)
    except LookupError:
        st.warning("Fallback NLTK : utilisation du tokenizer par défaut (anglais).")
        sentences = sent_tokenize(text)

    blocks = [' '.join(sentences[i:i + block_size]) for i in range(0, len(sentences), block_size)]

    s1_history, regimes, key_moments = [], [], []

    for i, block in enumerate(blocks):
        s1 = detect_s1(block, nlp)
        s1_history.append(s1)
        polarity = TextBlob(block).sentiment.polarity
        regime = classify_regime(s1_history, polarity)
        regimes.append(regime)

        if i > 1 and regime != regimes[i-1]:
            key_moments.append({
                "id": i + 1, "s1": s1, "regime": regime,
                "quote": block[:150] + ("..." if len(block) > 150 else ""),
                "polarity": round(polarity, 2)
            })

    return s1_history, regimes, key_moments
