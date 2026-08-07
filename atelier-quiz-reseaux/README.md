# SOS Maréchal-Ferrant — Atelier de quiz réseaux

Ce dépôt transforme un seul fichier de quiz en contenus directement publiables :

- quiz interactif GitHub Pages avec choix cliquables, corrections et score ;
- carrousel Facebook/Instagram en PNG 1080 × 1350 ;
- Reel Facebook, Reel Instagram et YouTube Short en MP4 1080 × 1920 ;
- compilation YouTube en MP4 1920 × 1080 ;
- textes de publication et sous-titres.

Le HTML interactif reste réservé à EquiCare, Systeme.io ou une page web. Facebook, Instagram et YouTube n'exécutent pas les boutons, le score ou le JavaScript d'un quiz HTML.

## Quiz interactif GitHub Pages

Le modèle `templates/quiz-interactif.html` fonctionne sans serveur et sans abonnement. Pour créer un nouveau quiz, copier ce fichier dans un dossier au nom du sujet et le renommer `index.html` :

```text
nom-du-quiz/index.html
```

Avec GitHub Pages publié depuis `main` et `/(root)`, son adresse devient :

```text
https://rico97440.github.io/quizz-chevaux/nom-du-quiz/
```

Ce lien peut être partagé sur Facebook. Le quiz s'ouvre alors comme une page web et conserve les choix cliquables, la correction, la navigation et le score final.

## Fonctionnement simple

1. Copier `contenus/modele-quiz.yaml` et remplacer le sujet et les questions.
2. Faire passer le contenu par les agents dans `agents/`.
3. Eric valide les passages terrain et la conduite à tenir.
4. Lancer `python scripts/render_quiz.py contenus/mon-quiz.yaml`.
5. Récupérer le dossier créé dans `exports/`.

Sur GitHub, l'action **Générer le pack quiz** fabrique la même chose automatiquement. Le ZIP final se télécharge dans les artefacts de l'action. Les fichiers MP4 destinés au public peuvent ensuite être placés dans une GitHub Release pour ne pas alourdir l'historique du dépôt.

## Format éditorial recommandé

Une question = une publication courte :

1. accroche ;
2. question et trois choix ;
3. pause de trois secondes ;
4. bonne réponse ;
5. explication courte ;
6. un seul appel à l'action.

Le même MP4 vertical sert à Facebook Reels, Instagram Reels et YouTube Shorts. Une compilation horizontale rassemble toutes les questions pour YouTube.

## Commandes

```bash
python -m pip install -r requirements.txt
python scripts/validate_quiz.py contenus/2026-08-07_observer-sans-diagnostiquer.yaml
python scripts/render_quiz.py contenus/2026-08-07_observer-sans-diagnostiquer.yaml
```

La génération demande Python 3.10+, Pillow, PyYAML et FFmpeg.

## Statuts

`idee` → `recherche` → `sources-a-valider` → `quiz-a-valider` → `validation-eric` → `securite-droits-ok` → `pret-a-generer` → `medias-a-controler` → `pret-a-publier` → `publie`

Le dépôt ne publie jamais automatiquement sur un réseau social. Le dernier geste reste volontaire.
