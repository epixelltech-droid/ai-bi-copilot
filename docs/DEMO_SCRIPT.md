# Demo entretien

Question : "Quel est le chiffre d'affaires par pays ?"

1. Le Router selectionne la source SQL.
2. Le SQL Agent produit une requete SELECT.
3. Le guardrail verifie qu'elle est read-only.
4. SQL execute la requete.
5. Le RAG ajoute les regles metier pertinentes.
6. L'Insight Agent synthetise le resultat.
7. L'audit trail conserve utilisateur, question, SQL, statut et latence.

Deuxieme scenario :
"Genere le DAX du chiffre d'affaires par pays dans Power BI."

Le Router selectionne Power BI et le DAX Agent produit une requete EVALUATE.
Avec les identifiants configures, elle est envoyee au semantic model.
