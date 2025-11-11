# psyscan_core_v2_5.py
# PSYSCAN v2.5
# Licence : AGPL-3.0
# Auteur : NAHT LIKE YOU THINK 

import streamlit as st
import nltk
from nltk.tokenize import sent_tokenize
from textblob import TextBlob
import spacy
from langdetect import detect, DetectorFactory
from collections import Counter
import re
import textwrap
from typing import Any, Dict, Tuple

DetectorFactory.seed = 0

# --- TÉLÉCHARGEMENT AUTOMATIQUE DES CORPUS NLTK ---
import nltk
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)

# --- NLTK ---
def ensure_nltk_data():
    for res in ['punkt_tab', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{res}' if res == 'punkt_tab' else f'corpora/{res}')
        except LookupError:
            nltk.download(res, quiet=True)
ensure_nltk_data()

# --- spaCy ---
LANG_MODELS = {'fr': 'fr_core_news_sm', 'en': 'en_core_web_sm'}

@st.cache_resource(show_spinner=False)
def load_spacy_model(lang_code: str):
    model_name = 'fr_core_news_sm' if lang_code == 'fr' else 'en_core_web_sm'
    try:
        return spacy.load(model_name)
    except Exception as e:
        st.warning(f"Modèle {model_name} manquant → téléchargement...")
        try:
            import subprocess, sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
            return spacy.load(model_name)
        except Exception as e2:
            st.error(f"Échec téléchargement : {e2}")
            return None

# --- STOPWORDS & ARTÉFACTS ---
ORAL_ARTIFACTS = {'euh', 'heu', 'hum', 'ah', 'bon', 'voilà', 'donc', 'alors', 'hein', 'ben', 'bah'}
STOPWORDS_FR = {
    'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'à', 'au', 'aux', 'en', 'dans', 'sur',
    'pour', 'par', 'avec', 'sans', 'mais', 'car', 'que', 'qui', 'quoi', 'dont', 'où', 'quand', 'si',
    'est', 'sont', 'a', 'avoir', 'être', 'tout', 'tous', 'toute', 'toutes', 'plus', 'moins', 'très',
    'peu', 'assez', 'aussi', 'encore', 'déjà', 'toujours', 'jamais', 'souvent', 'parfois', 'bientôt',
    'hier', 'aujourd’hui', 'demain', 'maintenant', 'alors', 'donc', 'car', 'mais', 'ni', 'si', 'comme',
    'lorsque', 'puisque', 'afin', 'parce', 'même', 'seulement', 'surtout', 'ainsi', 'enfin', 'bref',
    'voici', 'voilà', 'cependant', 'néanmoins', 'pourtant', 'd’ailleurs', 'en effet', 'en fait'
}

# --- CORPUS VULGUS v1.0 ---
VULGUS_CORPUS = {
    "ancrage": {
        "agir": "L'ordre d'agir comme un général",
        "travail": "L'obsession du travail comme devoir sacré",
        "refuser": "Le refus comme acte de survie",
        "puissance": "La puissance comme prothèse verbale",
        "peuple": "Le peuple comme bouclier collectif",
        "révolution": "La révolution comme fantasme répétitif",
        "écologie": "L'écologie comme mantra de survie",
        "sécurité": "La sécurité comme armure du pouvoir",
        "france": "La France comme totem national",
        "liberté": "La liberté comme mot-piège",
        "égalité": "L'égalité comme promesse répétée",
        "réforme": "La réforme comme fuite en avant",
        "crise": "La crise comme justification permanente",
        "avenir": "L'avenir comme horizon vide"
    },
    "fissure": {
        "nous_dominant": "Un sujet dissous dans le corps social pour éviter la singularité.",
        "je_isolé": "Un leader qui se cache derrière son mot fétiche.",
        "je_absent": "Un sujet effacé, remplacé par un 'nous' totalitaire.",
        "maturite": "Un leader qui endosse le 'Je' pour mieux engager le 'Nous'."
    },
    "projet": {
        "maitrise_directe": "Affirmer une direction sans le besoin de l'adhésion fusionnelle.",
        "suture_sociale": "Tenter de masquer la fragilité individuelle par la force du nombre."
    },
    "dependance": {
        "positif": "Si {s1} est détourné·e, le mythe vacille.",
        "négatif": "Si {s1} n'est pas surmonté·e, tout s'effondre.",
        "action": "Si l'action échoue, le discours devient ridicule.",
        "equilibre": "Le mot-clé est intégré et son échec est géré par la structure.",
        "refus_actif": "Si la contestation s'organise, l'identité discursive s'effondre.",
        "default": "Si {s1} perd son sens, le vide apparaît."
    },
    "risque": {
        "personne": "Un système qui s'est rendu dépendant de l'Homme-Providence.",
        "institution": "Un système qui s'est rendu dépendant de l'Homme-Providence.",
        "mot": "Un mot qui, s'il perd son sens, révèle le vide."
    },
    "conclusion": {
        "FORCLUSION": "Un pouvoir en forclusion — le réel est nié.",
        "SURRÉGIME": "Un pouvoir en surrégime — prêt à l'implosion.",
        "ATTENTION": "Un pouvoir fragile — tenu par un fil.",
        "STABLE": "Un pouvoir fondé sur le Réel — et non sur la répétition.",
        "CONFIANCE": "Un pouvoir fondé sur le Réel — et non sur la répétition."
    }
}

# --- FONCTIONS UTILITAIRES ---
def nettoyer_texte(texte: str) -> str:
    for artifact in ORAL_ARTIFACTS:
        texte = re.sub(rf'\b{artifact}\b', '', texte, flags=re.IGNORECASE)
    texte = re.sub(r'[^\w\s\.\?\!]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte).strip()
    return texte.lower()

def detect_s1_global(input_data: Any) -> Tuple[str, float, Counter]:
    """Traite texte brut OU doc spaCy"""
    if isinstance(input_data, str):
        words = [w.lower() for w in input_data.split() if w.isalpha() and len(w) > 2 and w not in STOPWORDS_FR]
    else:
        words = [t.lemma_.lower() for t in input_data if t.is_alpha and not t.is_stop and len(t.lemma_) > 2]
    freq = Counter(words)
    total = sum(freq.values())
    if total == 0:
        return "?", 0.0, freq
    s1, count = freq.most_common(1)[0]
    centralite = count / total
    return s1, centralite, freq

def compute_je_nous(text: str) -> Tuple[int, int, float]:
    je = len(re.findall(r'\bje\b', text.lower()))
    nous = len(re.findall(r'\bnous\b', text.lower()))
    ratio = nous / max(je, 1)
    return je, nous, ratio

def compute_psi(s1: str, centralite: float, count_s1: int, total: int) -> float:
    res1 = min(80 + count_s1 * 3, 99)
    res2 = min(75 + count_s1 * 2, 99)
    return round((centralite * 100 + res1 + res2) / 3, 1)

def polarite_s1(text: str, s1: str) -> str:
    blob = TextBlob(text)
    sentences = [s for s in blob.sentences if s1.lower() in s.lower()]
    if not sentences:
        return "neutre"
    polarity = sum(s.sentiment.polarity for s in sentences) / len(sentences)
    return "positif" if polarity > 0.1 else "négatif" if polarity < -0.1 else "neutre"

# --- ANALYSE COMPLÈTE ---
def analyze_discourse_v25(text: str, lang: str = "Français") -> Dict:
    lang_code = 'fr' if lang.lower().startswith('fr') else 'en'
    try:
        detected = detect(text[:500])
        if detected[:2] != lang_code:
            st.warning(f"Langue détectée : {detected} ≠ {lang}")
    except:
        pass

    nlp = load_spacy_model(lang_code)
    texte_net = nettoyer_texte(text)

    # --- S1 GLOBAL (Ψ stable) ---
    if nlp:
        doc = nlp(texte_net)
        s1, centralite, freq = detect_s1_global(doc)
    else:
        s1, centralite, freq = detect_s1_global(texte_net)
    
    total_mots = sum(freq.values())
    count_s1 = freq[s1]
    psi = compute_psi(s1, centralite, count_s1, total_mots)
    je, nous, ratio_nous_je = compute_je_nous(text)
    polarite = polarite_s1(text, s1)

    # --- SISMO ---
    nltk_lang = 'french' if lang_code == 'fr' else 'english'
    sentences = sent_tokenize(text, language=nltk_lang)
    block_size = 6
    blocks = [' '.join(sentences[i:i + block_size]) for i in range(0, len(sentences), block_size)]
    s1_history = []
    regimes = []
    key_moments = []
    
    for i, block in enumerate(blocks):
        block_net = nettoyer_texte(block)
        if nlp:
            block_doc = nlp(block_net)
            block_s1 = detect_s1_global(block_doc)[0]
        else:
            block_s1 = detect_s1_global(block_net)[0]
        s1_history.append(block_s1)
        polarity_val = TextBlob(block).sentiment.polarity
        changes = len(set(s1_history[-3:])) if len(s1_history) >= 3 else 1
        if changes == 1 and polarity_val > 0.1:
            regime = "centripète"
        elif changes >= 3 or polarity_val < -0.1:
            regime = "centrifuge"
        else:
            regime = "oscillant"
        regimes.append(regime)
        if i > 1 and regime != regimes[i-1]:
            key_moments.append({"id": i+1, "s1": block_s1, "regime": regime, "polarity": round(polarity_val, 2)})

    # --- RAPPORT ---
    icone = "FORCLUSION" if psi > 90 else "SURRÉGIME" if psi > 80 else "ATTENTION" if psi > 65 else "CONFIANCE" if psi < 50 else "STABLE"
    ancrage = VULGUS_CORPUS["ancrage"].get(s1, f"L'obsession de « {s1} » comme acte de pouvoir")
    fissure = (
        VULGUS_CORPUS["fissure"]["nous_dominant"] if ratio_nous_je > 3 else
        VULGUS_CORPUS["fissure"]["je_absent"] if je == 0 else
        VULGUS_CORPUS["fissure"]["maturite"] if 0.7 <= ratio_nous_je <= 1.3 and psi < 60 else
        VULGUS_CORPUS["fissure"]["je_isolé"]
    )
    projet = VULGUS_CORPUS["projet"]["suture_sociale"] if nous > 10 else VULGUS_CORPUS["projet"]["maitrise_directe"]
    rituel = f"Répéter « {s1} » {count_s1} fois pour faire taire le doute."
    contrat = f"Vous devez {s1} — sinon tout s'effondre."
    dependance = (
        VULGUS_CORPUS["dependance"]["equilibre"] if psi < 50 else
        VULGUS_CORPUS["dependance"]["refus_actif"] if s1 == "refuser" else
        VULGUS_CORPUS["dependance"]["positif"].format(s1=s1) if polarite == "positif" else
        VULGUS_CORPUS["dependance"]["négatif"].format(s1=s1) if polarite == "négatif" else
        VULGUS_CORPUS["dependance"]["action"]
    )
    risque = VULGUS_CORPUS["risque"]["institution"] if nous > je * 2 else VULGUS_CORPUS["risque"]["personne"]
    conclusion = VULGUS_CORPUS["conclusion"][icone]
    axiome = f"Le {s1.upper()} ({polarite}) suture la faille via la boucle collective."

    rapport = textwrap.dedent(f"""
    #### ANALYSE DE LA NARRATIVE INCONSCIENTE
    * **Mot-Clé Central (L'Ancrage) :** {ancrage} ({int(centralite*100)} %)
    * **La Fissure Révélée :** {fissure}
    * **Le Projet de Leadership :** {projet}
    ##### La Machine à Contrôle
    * **Fonction de la Répétition (Rituel) :** {rituel}
    * **Le Prix de l'Unité (Contrat) :** {contrat}
    ##### La Vulnérabilité du Récit
    * **Dépendance Critique :** {dependance}
    * **Le Risque Principal :** {risque}
    #### AXIO ME POÉTIQUE
    > *{axiome}*
    #### CONCLUSION : {icone}
    *{conclusion}*
    """).strip()

    return {
        's1': s1, 'psi': psi, 'centralite': centralite, 'polarite': polarite,
        'je': je, 'nous': nous, 'ratio_nous_je': ratio_nous_je,
        's1_history': s1_history, 'regimes': regimes, 'key_moments': key_moments,
        'rapport': rapport, 'axiome': axiome
    }
