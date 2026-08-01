from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.audit import read_audit_entries
from app.core.conversation_memory import clear_memory
from app.main import app

QUESTION_SET = [
    "Quel est le chiffre d'affaires total ?",
    "Quel est le chiffre d'affaires par pays ?",
    "Montre moi le CA cote pays stp",
    "Quel pays vend le mieux ?",
    "Quel est le chiffre d'affaires par mois ?",
    "Et en 2026 ?",
    "Quels sont les 10 meilleurs clients ?",
    "Qui vend le mieux en enterprise ?",
    "Quelle est la marge par categorie ?",
    "Compare la marge entre la France et le Maroc.",
    "Affiche les ventes de janvier 2025",
    "Que signifie Revenue ?",
    "Comment calcule-t-on la marge ?",
    "Explique moi la marge en version simple",
    "Que veut dire SMB ?",
    "Qu'est-ce qu'un client Enterprise ?",
    "Comment est defini un top product ?",
    "Quelle est la difference entre Revenue et Margin ?",
    "A quoi correspond le pays dans les analyses ?",
    "Que signifie EBITDA ?",
]


def main() -> None:
    client = TestClient(app)
    user_id = "openai-eval-user"
    clear_memory(user_id)

    for index, question in enumerate(QUESTION_SET, start=1):
        response = client.post(
            "/api/chat",
            json={"question": question, "user_id": user_id, "source": "auto"},
        )
        body = response.json()
        history = read_audit_entries(user_id=user_id, limit=1)
        hybrid_meta = history[0].get("hybrid_meta", {}) if history else {}
        answer = str(body.get("answer", "")).replace("\n", " | ")

        print(f"Q{index}: {question}")
        print(
            "  "
            f"status={response.status_code} "
            f"route={body.get('route')} "
            f"lang={body.get('artifact', {}).get('language')}"
        )
        print(f"  answer={answer[:260]}")
        print(f"  hybrid_meta={hybrid_meta}")
        print("---")


if __name__ == "__main__":
    main()
