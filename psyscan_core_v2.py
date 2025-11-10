# psyscan_core_v2.py
import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st

# --- NLTK : Téléchargement sécurisé ---
def ensure_nltk_data():
    resources = ['punkt_tab', 'stopwords']
    for res in resources:
        try:
            nltk.data.find(f'tokenizers/{res}' if res == 'punkt_tab' else f'corpora/{res}')
        except LookupError:
            nltk.download(res, quiet=True)

ensure_nltk_data()

# --- spaCy ---
LANG_MODELS = {'fr': 'fr_core_news_sm', 'en': 'en_core_web_sm'}

@st.cache_resource
def load_spacy_model(lang_code):
    model_name = LANG_MODELS.get(lang_code, LANG_MODELS['fr'])
    try:
        return spacy.load(model_name)
    except Exception as e:
        st.error(f"Modèle spaCy `{model_name}` introuvable.")
        st.info("Fallback NLTK activé (S1 instable en français).")
        return None  # → on passe en mode dégradé

def analyze_discourse(text, lang='Français', block_size=5):
    lang_code = 'fr' if lang.lower().startswith('fr') else 'en'
    
    # --- 1. spaCy (cerveau) ---
    nlp = load_spacy_model(lang_code)
    
    # --- 2. NLTK (découpage phrases) ---
    try:
        sentences = sent_tokenize(text, language=lang_code)
    except:
        st.warning("Tokenizer NLTK échoué → fallback anglais.")
        sentences = sent_tokenize(text, language='english')  # Fallback

    blocks = [' '.join(sentences[i:i + block_size]) for i in range(0, len(sentences), block_size)]
    
    s1_history, regimes, key_moments = [], [], []

    for i, block in enumerate(blocks):
        if nlp is not None:
            # MODE NORMAL : spaCy actif
            doc = nlp(block)
            tokens = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop]
            s1 = nltk.FreqDist(tokens).most_common(1)[0][0] if tokens else "?"
        else:
            # MODE DÉGRADÉ : spaCy HS → fallback brut
            words = block.lower().split()
            words = [w for w in words if w.isalpha() and w not in ['le', 'la', 'de', 'et', 'pour']]
            s1 = nltk.FreqDist(words).most_common(1)[0][0] if words else "?"

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

def classify_regime(s1_history, polarity):
    if len(s1_history) < 2: return "?"
    changes = len(set(s1_history[-3:]))
    if changes == 1 and polarity > 0.1: return "centripète"
    if changes >= 3 or polarity < -0.1: return "centrifuge"
    return "centré (oscillant)"
