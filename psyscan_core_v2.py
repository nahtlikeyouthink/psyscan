import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st

# --- AJOUT DE LA LOGIQUE DE GESTION DES MODÈLES SPAÇY POUR STREAMLIT CLOUD ---
from spacy.util import get_installed_pipes

LANG_MODELS = {
    'fr': 'fr_core_news_sm',
    'en': 'en_core_web_sm'
}
DEFAULT_MODEL = 'fr_core_news_sm'

# Vérification et téléchargement des modèles nécessaires
for lang_code, model_name in LANG_MODELS.items():
    if model_name not in get_installed_pipes():
        print(f"Téléchargement du modèle spaCy : {model_name}...")
        try:
            # Cette méthode est supportée par Streamlit pour les installations temporaires
            spacy.cli.download(model_name)
            print(f"Modèle {model_name} téléchargé avec succès.")
        except Exception as e:
            st.error(f"Erreur critique lors du téléchargement de {model_name}: {e}")

# --- FIN DE LA LOGIQUE DE GESTION DES MODÈLES ---


def detect_s1(block, nlp):
    """Signifiant maître (S1) par fréquence + lemmatisation."""
    # ... (le reste de la fonction est inchangé)
    tokens = [t.lemma_.lower() for t in nlp(block) if t.is_alpha and not t.is_stop]
    freq = nltk.FreqDist(tokens)
    return freq.most_common(1)[0][0] if freq else "?"

def classify_regime(s1_history, polarity):
    """Topologie : centripète / centré / centrifuge."""
    # ... (le reste de la fonction est inchangé)
    if len(s1_history) < 2: return "?"
    changes = len(set(s1_history[-3:]))
    if changes == 1 and polarity > 0.1: return "centripète"
    if changes >= 3 or polarity < -0.1: return "centrifuge"
    return "centré (oscillant)"

# Utilisation du cache de Streamlit pour éviter de charger le modèle à chaque appel
@st.cache_resource
def load_spacy_model(model_name):
    """Charge le modèle spaCy avec mise en cache Streamlit."""
    try:
        # Tente de charger le modèle après la vérification/téléchargement initial
        return spacy.load(model_name)
    except OSError:
        st.error(f"Le modèle spaCy '{model_name}' n'a pas pu être chargé.")
        return None


def analyze_discourse(text, lang='fr', block_size=5):
    """Analyse complète : temps réel + rétrospective."""
    # Détection langue
    try:
        detected = detect(text[:500])
        if detected[:2] != lang[:2]:
            st.warning(f"Langue détectée : **{detected}** ≠ **{lang}** → S1 peut être instable.")
    except: pass

    # Utilisation du modèle chargé via la fonction de cache
    selected_model_name = LANG_MODELS.get(lang[:2], DEFAULT_MODEL)
    nlp = load_spacy_model(selected_model_name)
    
    # Gérer le cas où le modèle n'a pas pu être chargé
    if nlp is None:
        return [], [], []

    sentences = sent_tokenize(text)
    # ... (le reste de la fonction est inchangé)
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
