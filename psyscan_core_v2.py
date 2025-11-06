import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st

# Modèles spaCy (télécharge si besoin)
LANG_MODELS = {
    'fr': 'fr_core_news_sm',
    'en': 'en_core_web_sm'
}

def detect_s1(block, nlp):
    """Signifiant maître (S1) par fréquence + lemmatisation."""
    tokens = [t.lemma_.lower() for t in nlp(block) if t.is_alpha and not t.is_stop]
    freq = nltk.FreqDist(tokens)
    return freq.most_common(1)[0][0] if freq else "?"

def classify_regime(s1_history, polarity):
    """Topologie : centripète / centré / centrifuge."""
    if len(s1_history) < 2: return "?"
    changes = len(set(s1_history[-3:]))
    if changes == 1 and polarity > 0.1: return "centripète"
    if changes >= 3 or polarity < -0.1: return "centrifuge"
    return "centré (oscillant)"

def analyze_discourse(text, lang='fr', block_size=5):
    """Analyse complète : temps réel + rétrospective."""
    # Détection langue
    try:
        detected = detect(text[:500])
        if detected[:2] != lang[:2]:
            st.warning(f"Langue détectée : **{detected}** ≠ **{lang}** → S1 peut être instable.")
    except: pass

    nlp = spacy.load(LANG_MODELS.get(lang[:2], 'fr_core_news_sm'))
    sentences = sent_tokenize(text)
    blocks = [' '.join(sentences[i:i+block_size]) for i in range(0, len(sentences), block_size)]

    s1_history, regimes, key_moments = [], [], []
    for i, block in enumerate(blocks):
        s1 = detect_s1(block, nlp)
        s1_history.append(s1)
        polarity = TextBlob(block).sentiment.polarity
        regime = classify_regime(s1_history, polarity)
        regimes.append(regime)

        # Marqueur si rupture
        if i > 1 and regime != regimes[i-1]:
            key_moments.append({
                "id": i+1, "s1": s1, "regime": regime,
                "quote": block[:150] + "...", "polarity": round(polarity, 2)
            })

    return s1_history, regimes, key_moments
