# Demo entretien

Question : "Quel est le chiffre d'affaires par pays ?"

1. Le Router selectionne la source SQL.
2. Le SQL Agent produit une requete SELECT.
3. Le guardrail verifie qu'elle est read-only.
4. SQL execute la requete.
5. L'Insight Agent synthetise le resultat.
6. L'audit trail conserve utilisateur, question, SQL, statut et latence.

Scenario documentaire :

Question : "Comment calcule-t-on la marge ?"

1. Le Router selectionne la source RAG.
2. Le retriever local cherche dans `knowledge_base/`.
3. Les passages les plus pertinents sont recuperes.
4. Le moteur RAG construit une reponse courte.
5. Les sources documentaires sont retournees dans la reponse.

Deuxieme scenario :
"Genere le DAX du chiffre d'affaires par pays dans Power BI."

Le Router selectionne Power BI et le DAX Agent produit une requete EVALUATE.
Avec les identifiants configures, elle est envoyee au semantic model.
