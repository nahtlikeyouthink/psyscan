import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect
import streamlit as st
# Importe la fonction de téléchargement spacy.cli.download
from spacy.cli import download as spacy_download 

# Modèles spaCy 
LANG_MODELS = {
    'fr': 'fr_core_news_sm',
    'en': 'en_core_web_sm'
}

# --- BLOC DE GESTION/TÉLÉCHARGEMENT DES MODÈLES SPAÇY (Exécuté au démarrage) ---
# Ceci remplace la méthode utilisant get_installed_pipes qui causait l'erreur.
for lang_code, model_name in LANG_MODELS.items():
    try:
        # Tente de charger le modèle. Si le modèle n'est pas trouvé, lève une OSError.
        spacy.load(model_name)
    except OSError:
        print(f"Téléchargement du modèle spaCy manquant : {model_name}...")
        try:
            # Télécharge le modèle en utilisant l'utilitaire spacy.cli
            spacy_download(model_name)
            print(f"Modèle {model_name} téléchargé avec succès.")
        except Exception as e:
            # Affiche une erreur Streamlit si le téléchargement échoue
            st.error(f"Erreur critique lors du téléchargement de {model_name}: {e}")
# --- FIN DU BLOC ---

def detect_s1(block, nlp):
    """Signifiant maître (S1) par fréquence + lemmatisation."""
    # Assurez-vous que les dépendances NLTK sont chargées si nécessaire (ici on suppose 'punkt' pour sent_tokenize)
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

# Utilisation du cache de Streamlit pour éviter de charger le modèle à chaque appel
@st.cache_resource
def load_spacy_model(model_name):
    """Charge le modèle spaCy avec mise en cache Streamlit."""
    try:
        return spacy.load(model_name)
    except OSError:
        # L'erreur est gérée ici au cas où le modèle n'ait pas été téléchargé par le bloc initial
        st.error(f"Le modèle spaCy '{model_name}' n'a pas pu être chargé. Redéploiement requis.")
        return None


def analyze_discourse(text, lang='fr', block_size=5):
    """Analyse complète : temps réel + rétrospective."""
    # Détection langue
    try:
        detected = detect(text[:500])
        if detected[:2] != lang[:2]:
            st.warning(f"Langue détectée : **{detected}** ≠ **{lang}** → S1 peut être instable.")
    except: 
        pass # Ignorer si la détection de langue échoue

    # Utilisation du modèle chargé via la fonction de cache
    selected_model_name = LANG_MODELS.get(lang[:2], 'fr_core_news_sm')
    nlp = load_spacy_model(selected_model_name)
    
    # Gérer le cas où le modèle n'a pas pu être chargé
    if nlp is None:
        return [], [], []

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
