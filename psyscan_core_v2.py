# psyscan_core_v2.py
import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st
from collections import Counter

# --- NLTK : Téléchargement sécurisé ---
def ensure_nltk_data():
    for res in ['punkt_tab', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{res}' if res == 'punkt_tab' else f'corpora/{res}')
        except LookupError:
            nltk.download(res, quiet=True)

ensure_nltk_data()

# --- Mapping langue NLTK ---
NLTK_LANGUAGES = {
    'fr': 'french',
    'en': 'english'
}

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
        return None

def detect_s1(block, nlp):
    if nlp is None:
        words = [w.lower() for w in block.split() if w.isalpha()]
        words = [w for w in words if w not in ['le', 'la', 'de', 'et', 'pour', 'dans', 'un', 'une']]
        freq = nltk.FreqDist(words)
        return freq.most_common(1)[0][0] if freq else "?"
    else:
        tokens = [t.lemma_.lower() for t in nlp(block) if t.is_alpha and not t.is_stop]
        freq = nltk.FreqDist(tokens)
        return freq.most_common(1)[0][0] if freq else "?"

def classify_regime(s1_history, polarity):
    if len(s1_history) < 2: return "?"
    changes = len(set(s1_history[-3:]))
    if changes == 1 and polarity > 0.1: return "centripète"
    if changes >= 3 or polarity < -0.1: return "centrifuge"
    return "centré (oscillant)"

def analyze_discourse(text, lang='Français', block_size=5):
    lang_code = 'fr' if lang.lower().startswith('fr') else 'en'
    nltk_lang = NLTK_LANGUAGES.get(lang_code, 'english')

    try:
        detected = detect(text[:500])
        if detected[:2] != lang_code:
            st.warning(f"Langue détectée : **{detected}** ≠ **{lang}**")
    except:
        pass

    nlp = load_spacy_model(lang_code)

    # --- TOKENISATION ROBUSTE ---
    try:
        sentences = sent_tokenize(text, language=nltk_lang)
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
        try:
            sentences = sent_tokenize(text, language=nltk_lang)
        except:
            st.warning(f"Tokenizer `{nltk_lang}` indisponible → fallback anglais.")
            sentences = sent_tokenize(text, language='english')
    except Exception:
        st.warning("Erreur NLTK → fallback anglais.")
        sentences = sent_tokenize(text, language='english')

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

    # === CALCUL DE L'INDICE Ψ ===
    s1_freq = Counter(s1_history)
    total = len(s1_history)
    psi = max(s1_freq.values()) / total if total > 0 else 0

    return s1_history, regimes, key_moments, round(psi, 3)
