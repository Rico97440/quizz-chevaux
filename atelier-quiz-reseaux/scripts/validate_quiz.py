#!/usr/bin/env python3
import sys
from pathlib import Path
import yaml


STATUSES = {
    "idee", "recherche", "sources-a-valider", "quiz-a-valider",
    "validation-eric", "securite-droits-ok", "pret-a-generer",
    "medias-a-controler", "pret-a-publier", "publie",
}


def validate(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = []
    for key in ("titre", "serie", "statut", "cta", "questions"):
        if not data.get(key):
            errors.append(f"champ obligatoire absent : {key}")
    if data.get("statut") not in STATUSES:
        errors.append("statut inconnu")
    for index, q in enumerate(data.get("questions", []), start=1):
        prefix = f"question {index}"
        if len(q.get("choix", [])) != 3:
            errors.append(f"{prefix} : exactement 3 choix sont requis")
        if q.get("bonne_reponse") not in (1, 2, 3):
            errors.append(f"{prefix} : bonne_reponse doit valoir 1, 2 ou 3")
        for key in ("id", "question", "explication", "source_ids"):
            if key not in q:
                errors.append(f"{prefix} : champ absent {key}")
    if errors:
        raise ValueError("\n".join(errors))
    return data


if __name__ == "__main__":
    quiz_path = Path(sys.argv[1])
    quiz = validate(quiz_path)
    print(f"OK — {len(quiz['questions'])} question(s) : {quiz['titre']}")

