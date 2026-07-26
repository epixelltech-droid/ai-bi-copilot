from app.agents.router import route_question


def test_sql():
    assert route_question("Quel est le CA par pays ?") == "sql"


def test_powerbi():
    assert route_question("Genere une requete DAX Power BI") == "powerbi"


def test_rag():
    assert route_question("Quelle est la definition de la marge ?") == "rag"


def test_rag_enterprise_definition():
    assert route_question("Qu'est-ce qu'un client Enterprise ?") == "rag"


def test_rag_difference_question():
    assert route_question("Quelle est la difference entre Revenue et Margin ?") == "rag"
