# PSYSCAN (v1.0) - README 
PSYSCAN révèle la structure du pouvoir — pas les individus.

**Author** / Auteur : Naht Like You Think

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17504541.svg)](https://doi.org/10.5281/zenodo.17504541)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

---

### Sismographe du Discours Politique

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://psyscan-nn4rgzvcuajg562b4opbu3.streamlit.app/)

**Lancer l'Analyse :** Le badge ci-dessus mène à l'interface utilisateur (Streamlit Cloud), permettant l'analyse de discours en temps réel sans aucune installation.

---

### Résumé

PSYSCAN révèle la structure du pouvoir — pas les individus. L'outil est un sismographe du discours qui part du postulat psychanalytique (Lacan) que le discours politique est pulsionnel et organisé autour d'un Signifiant-Maître (S1).Méthode (FR)

Outil open-source d’analyse formelle du discours (TALN). Il détecte le Signifiant-Maître (S1), mesure sa centralité et sa résistance au bruit, et génère un rapport interprétatif nuancé (via l'Indice Ψ), révélant la stabilité structurelle du pouvoir.

ÉthiqueL'outil est conçu comme un instrument de vérité publique : libre, éthique (AGPL-3.0), et focalisé sur les structures plutôt que sur l'interprétation individuelle.


---

### Licence & Ethics / Licence & Éthique

This software is distributed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**, ensuring code freedom and transparency (strong Copyleft).

 **IMPORTANT:** The use of this software is **strictly conditional** upon adherence to the **Ethical Guidelines** detailed in the accompanying file: [`ETHICAL_GUIDELINES.md`](ETHICAL_GUIDELINES.md).

> **In short:** Free for research and the analysis of **public** discourse — **Strictly forbidden** for profiling, individual surveillance, or use in Human Resources (HR).

> **En bref :** Libre pour la recherche et l'analyse de discours **publics** — **Strictement interdit** pour le profilage, la surveillance individuelle ou l'usage en Ressources Humaines (RH).

---

### Installation (Local)

```bash
git clone [https://github.com/nahtlikeyouthink/psyscan.py](https://github.com/nahtlikeyouthink/psyscan.py)
cd psyscan

# Création de l'environnement
python3 -m venv venv

# Activation de l'environnement (Linux/macOS) :
source venv/bin/activate
# Activation de l'environnement (Windows PowerShell) :
.\venv\Scripts\Activate

pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('vader_lexicon')"

```
---

### Citation

If you use this work in a publication, please cite the Zenodo archive via its DOI:

**NAHT LIKE YOU THINK. (2025). *PSYSCAN v1.0*. Zenodo. DOI: 10.5281/zenodo.17504541**

---

### References / Références

* [Full License (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.txt)
* [Detailed Ethical Guidelines](ETHICAL_GUIDELINES.md)

  
