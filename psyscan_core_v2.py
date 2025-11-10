import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st

# --- CONFIG ---
LANG_MODELS = {
    'fr': 'fr_core_news_sm',
    'en': 'en_core_web_sm'
}

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
def load_spacy_model(model_name):
    """Charge un modèle pré-installé via pip."""
    try:
        return spacy.load(model_name)
    except OSError as e:
        st.error(f"Modèle `{model_name}` non trouvé. Assurez-vous qu'il est dans `requirements.txt`.")
        raise e

def analyze_discourse(text, lang='fr', block_size=5):
    # Détection langue
    try:
        detected = detect(text[:500])
        if detected[:2] != lang[:2]:
            st.warning(f"Langue détectée : **{detected}** ≠ **{lang}** → S1 peut être instable.")
    except:
        pass

    # Sélection du modèle
    model_name = LANG_MODELS.get(lang[:2], LANG_MODELS['fr'])
    
    # Chargement du modèle
    nlp = load_spacy_model(model_name)

    # Tokenisation en phrases
    sentences = sent_tokenize(text, language=lang[:2])
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
                "quote": block[:150] + ("..." if len(block) > 150 else ""),
                "polarity": round(polarity, 2)
            })

    return s1_history, regimes, key_moments

# --- INTERFACE STREAMLIT ---
st.title("Analyse Discursive - S1 & Régime")

lang = st.selectbox("Langue", ["fr", "en"], format_func=lambda x: "Français" if x == "fr" else "English")
text = st.text_area("Texte à analyser", height=200, placeholder="Collez votre texte ici...")

if st.button("Analyser"):
    if not text.strip():
        st.error("Veuillez entrer un texte.")
    else:
        with st.spinner("Analyse en cours..."):
            s1_history, regimes, key_moments = analyze_discourse(text, lang=lang)

        st.subheader("Évolution du S1")
        st.line_chart([i for i in range(len(s1_history))], use_container_width=True)
        st.write("S1 par bloc :", s1_history)

        st.subheader("Régime discursif")
        st.write(regimes)

        if key_moments:
            st.subheader("Moments clés de bascule")
            for m in key_moments:
                st.markdown(f"**Bloc {m['id']}** → `{m['regime']}` (S1: `{m['s1']}`, polarité: {m['polarity']})")
                st.caption(m['quote'])
        else:
            st.info("Aucun changement de régime détecté.")
