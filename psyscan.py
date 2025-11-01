# psyscan.py
# PSYSCAN v1.0 – Scanner méta-psychique du discours public
# PSYSCAN révèle la structure du pouvoir — pas les individus
# Licence : AGPL-3.0 + ETHICAL_GUIDELINES.md
# Auteur : NAHT LIKE YOU THINK – DOI : 10.5281/zenodo.xxxxxxx

import re
import nltk
from collections import Counter, defaultdict
import textwrap
from typing import List, Dict

# === TÉLÉCHARGEMENT NLTK (exécuter une fois) ===
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('wordnet')
# nltk.download('omw-1.4')
# nltk.download('vader_lexicon')
# pip install textblob

from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, ne_chunk
from textblob import TextBlob

# ========================
# CONFIG & STOPWORDS
# ========================
STOPWORDS = set(stopwords.words('french'))
STOPWORDS.update({
  'les', 'des', 'du', 'au', 'aux', 'et', 'ou', 'par', 'pour', 'dans', 'sur', 'avec', 'sans',
  'sous', 'vers', 'depuis', 'jusqu', 'après', 'avant', 'pendant', 'entre', 'contre', 'malgré',
  'grâce', 'chez', 'près', 'loin', 'ici', 'là', 'où', 'quand', 'comment', 'pourquoi', 'qui',
  'que', 'quoi', 'dont', 'lequel', 'laquelle', 'lesquels', 'lesquelles', 'celui', 'celle',
  'ceux', 'celles', 'tout', 'tous', 'toute', 'toutes', 'plus', 'moins', 'très', 'trop',
  'peu', 'assez', 'autant', 'aussi', 'encore', 'déjà', 'toujours', 'jamais', 'souvent',
  'rarement', 'parfois', 'quelquefois', 'bientôt', 'tard', 'hier', 'aujourd’hui', 'demain',
  'maintenant', 'alors', 'donc', 'car', 'mais', 'ni', 'si', 'comme', 'lorsque', 'puisque',
  'quoique', 'afin', 'parce', 'même', 'seulement', 'surtout', 'notamment', 'ainsi', 'enfin',
  'finalement', 'bref', 'voici', 'voilà', 'cependant', 'néanmoins', 'pourtant', 'toutefois',
  'd’ailleurs', 'en effet', 'en réalité', 'en fait', 'autrement dit', 'c’est-à-dire'
})

ORAL_ARTIFACTS = {'euh', 'heu', 'hum', 'ah', 'bon', 'voilà', 'donc', 'alors', 'hein', 'ben', 'bah'}

# ========================
# LEMMATISATION
# ========================
lemmatizer = WordNetLemmatizer()
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('V'): return wordnet.VERB
    elif treebank_tag.startswith('N'): return wordnet.NOUN
    elif treebank_tag.startswith('J'): return wordnet.ADJ
    elif treebank_tag.startswith('R'): return wordnet.ADV
    else: return wordnet.NOUN
            
# ========================
# NER
# ========================
def extract_entities(text: str) -> set:
  try:
    chunked = ne_chunk(pos_tag(nltk.word_tokenize(text)))
    entities = set()
    for chunk in chunked:
      if hasattr(chunk, 'label'):
        entity = ' '.join(c[0] for c in chunk)
        entities.add(entity.lower())
        return entities

  except:
    return set()

# ========================
# CORPUS VULGUS v1.0
# ========================
VULGUS_CORPUS = {
  "ancrage": {
    "agir": "L’ordre d’agir comme un général",
    "travail": "L’obsession du travail comme devoir sacré",
    "refuser": "Le refus comme acte de survie",
    "puissance": "La puissance comme prothèse verbale",
    "peuple": "Le peuple comme bouclier collectif",
    "révolution": "La révolution comme fantasme répétitif",
    "écologie": "L’écologie comme mantra de survie",
    "sécurité": "La sécurité comme armure du pouvoir",
    "france": "La France comme totem national",
    "liberté": "La liberté comme mot-piège",
    "égalité": "L’égalité comme promesse répétée",
    "réforme": "La réforme comme fuite en avant",
    "crise": "La crise comme justification permanente",
    "avenir": "L’avenir comme horizon vide"
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
    "négatif": "Si {s1} n’est pas surmonté·e, tout s’effondre.",
    "action": "Si l’action échoue, le discours devient ridicule.",
    "equilibre": "Le mot-clé est intégré et son échec est géré par la structure.",
    "refus_actif": "Si la contestation s’organise, l’identité discursive s’effondre.",
    "default": "Si {s1} perd son sens, le vide apparaît."
  },
  "risque": {
    "personne": "Un système qui s’est rendu dépendant de l’Homme-Providence.",
    "institution": "Un système qui s’est rendu dépendant de l’Homme-Providence.",
    "mot": "Un mot qui, s’il perd son sens, révèle le vide."
  },
  "conclusion": {
    "FORCLUSION": "Un pouvoir en forclusion — le réel est nié.",
    "SURRÉGIME": "Un pouvoir en surrégime — prêt à l’implosion.",
    "ATTENTION": "Un pouvoir fragile — tenu par un fil.",
    "STABLE": "Un pouvoir fondé sur le Réel — et non sur la répétition.",
    "CONFIANCE": "Un pouvoir fondé sur le Réel — et non sur la répétition."
  }
}

# ========================
# CLASSE PSYSCAN
# ========================
class PSYSCAN:
  def __init__(self):
    pass

def nettoyer_texte(self, texte: str) -> str:

  for artifact in ORAL_ARTIFACTS:
    texte = re.sub(rf'\b{artifact}\b', '', texte, flags=re.IGNORECASE)
    texte = re.sub(r'[^\w\s\.\?\!]', ' ', texte)
    texte = re.sub(r'\s+', ' ', texte).strip()
    return texte.lower()

def lemmatiser(self, tokens: List[str]) -> List[str]:
  tagged = pos_tag(tokens)
  return [
    lemmatizer.lemmatize(word, get_wordnet_pos(tag))
    for word, tag in tagged
  ]

def filtrer_ner(self, tokens: List[str], entities: set) -> List[str]:
  return [t for t in tokens if t not in entities and len(t) > 2 and t not in STOPWORDS]

def cooccurrence(self, tokens: List[str], s1: str, window: int = 5) -> List[str]:
  indices = [i for i, t in enumerate(tokens) if t == s1]
  coocs = defaultdict(int)
for idx in indices:
  start = max(0, idx - window)
  end = min(len(tokens), idx + window + 1)
  context = tokens[start:idx] + tokens[idx+1:end]
for word in context:
  if word != s1 and word not in STOPWORDS:
    coocs[word] += 1
    return [word for word, _ in sorted(coocs.items(), key=lambda x: x[1], reverse=True)[:2]]
def polarite_s1(self, texte: str, s1: str) -> str:
  blob = TextBlob(texte)
  sentences_with_s1 = [s for s in blob.sentences if s1 in s.lower()]
  
if not sentences_with_s1:
  return "neutre"
  polarity = sum(s.sentiment.polarity for s in sentences_with_s1) / len(sentences_with_s1)
  return "positif" if polarity > 0.1 else "négatif" if polarity < -0.1 else "neutre"

# === ÉTAPE 1 : Ψ-SCAN ===
def psi_scan(self, texte: str) -> dict:
global texte_global
texte_global = texte

texte_net = self.nettoyer_texte(texte)
tokens = nltk.word_tokenize(texte_net, language='french')
entities = extract_entities(texte)
lemmas = self.lemmatiser(tokens)
filtered = self.filtrer_ner(lemmas, entities)

freq = Counter(filtered)
total = sum(freq.values())
if total == 0:
return {'error': 'Aucun mot significatif détecté'}

top = freq.most_common(5)
s1, count_s1 = top[0]
centralite = round((count_s1 / total) * 100, 1)
coocs = self.cooccurrence(filtered, s1)

je = len(re.findall(r'\bje\b', texte.lower()))
nous = len(re.findall(r'\bnous\b', texte.lower()))
ratio_nous_je = nous / max(je, 1)

res1 = min(80 + count_s1 * 3, 99)
res2 = min(75 + count_s1 * 2, 99)
indice_psi = round((centralite + res1 + res2) / 3, 1)
polarite = self.polarite_s1(texte, s1)

return {
's1': s1,
'centralite': centralite,
'top_mots': [w for w, _ in top[:3]],
'coocs': coocs,
'je': je,
'nous': nous,
'ratio_nous_je': round(ratio_nous_je, 1),
'resistance1': res1,
'resistance2': res2,
'indice_psi': indice_psi,
'polarite': polarite,
'total_mots': total
}

# === ÉTAPE 2 : Ψ-LOGUE ===
def psi_logue(self, scan: dict) -> dict:
s1 = scan['s1']
boucle = ' → '.join(scan['coocs']) if scan['coocs'] else ' → '.join(scan['top_mots'][1:3])
faille = f"glissement je→nous ({scan['je']}→{scan['nous']})"
polarite = scan['polarite']
axiome = f"Le {s1.upper()} ({polarite}) suture la faille via la boucle {boucle}."
return {'axiome': axiome, 'boucle': boucle}

# === ÉTAPE 3 : Ψ-VULGUS v1.0 ===
def psi_vulgus(self, scan: dict, logue: dict, titre: str = "") -> str:
C = VULGUS_CORPUS
s1 = scan['s1']
indice = scan['indice_psi']
polarite = scan['polarite']
ratio = scan['ratio_nous_je']

# === ICÔNE NUANCÉE ===
if indice > 90:
icone = "FORCLUSION"
elif indice > 80:
icone = "SURRÉGIME"
elif indice > 65:
icone = "ATTENTION"
elif indice < 50:
icone = "CONFIANCE"
else:
icone = "STABLE"

# === ANCRAGE ===
ancrage = C["ancrage"].get(s1, f"L’obsession de « {s1} » comme acte de pouvoir")

# === FISSURE (avec maturité) ===
if ratio > 3:
fissure = C["fissure"]["nous_dominant"]
elif scan['je'] == 0:
fissure = C["fissure"]["je_absent"]
elif 0.7 <= ratio <= 1.3 and indice < 60:
fissure = C["fissure"]["maturite"]
else:
fissure = C["fissure"]["je_isolé"]

# === PROJET ===
if scan['nous'] > 10:
projet = C["projet"]["suture_sociale"]
else:
projet = C["projet"]["maitrise_directe"]

# === RITUEL ===
count_s1 = len(re.findall(rf'\b{s1}\b', texte_global.lower()))
rituel = f"Répéter « {s1} » {count_s1} fois pour faire taire le doute."

# === CONTRAT ===
contrat = f"Vous devez {s1} — sinon tout s’effondre."

# === DÉPENDANCE (équilibre si stable) ===
if indice < 50:
dependance = C["dependance"]["equilibre"]
elif s1 == "refuser":
dependance = C["dependance"]["refus_actif"]
elif polarite == "positif":
dependance = C["dependance"]["positif"].format(s1=s1)
elif polarite == "négatif":
dependance = C["dependance"]["négatif"].format(s1=s1)
else:
dependance = C["dependance"]["action"]

# === RISQUE ===
risque = C["risque"]["institution"] if scan['nous'] > scan['je'] * 2 else C["risque"]["personne"]

# === CONCLUSION ===
conclusion = C["conclusion"][icone]

rapport = f"""[Rapport PSYSCAN v1.0]{titre}

#### ANALYSE DE LA NARRATIVE INCONSCIENTE DU DISCOURS

* **Mot-Clé Central (L'Ancrage) :** {ancrage} ({int(scan['centralite'])} %)
* **La Fissure Révélée (La Problématique) :** {fissure}
* **Le Projet de Leadership :** {projet}

##### La Machine à Contrôle
* **Fonction de la Répétition (Rituel) :** {rituel}
* **Le Prix de l'Unité (Le Contrat Social) :** {contrat}

##### La Vulnérabilité du Récit
* **Dépendance Critique :** {dependance}
* **Le Risque Principal :** {risque}

#### CONCLUSION : L'ÉTAT ÉMOTIONNEL DU POUVOIR
* {icone} {conclusion}
"""

return textwrap.dedent(rapport).strip()

# === FONCTION PRINCIPALE ===
def analyser(self, texte: str, titre: str = "") -> str:
global texte_global
texte_global = texte
scan = self.psi_scan(texte)
if 'error' in scan:
return f"Erreur : {scan['error']}"
logue = self.psi_logue(scan)
return self.psi_vulgus(scan, logue, titre)


# ========================
# EXÉCUTION
# ========================
if __name__ == "__main__":
scanner = PSYSCAN()
print("PSYSCAN v1.0 – Entrez le discours (Ctrl+D pour terminer) :\n")
lignes = []
try:
while True:
ligne = input()
lignes.append(ligne)
except EOFError:
pass
discours = "\n".join(lignes).strip()
if discours:
print("\n" + scanner.analyser(discours, "Discours analysé"))
else:
print("Aucun texte saisi.")
