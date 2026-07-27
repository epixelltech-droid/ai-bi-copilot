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


def test_sql_short_revenue_variant():
    assert route_question("CA par pays") == "sql"


def test_sql_monthly_revenue_variant():
    assert route_question("revenu mensuel") == "sql"


def test_rag_definition_margin_variant():
    assert route_question("definition de margin") == "rag"


def test_rag_c_est_quoi_revenue_variant():
    assert route_question("c'est quoi revenue") == "rag"


def test_rag_que_veut_dire_smb_variant():
    assert route_question("Que veut dire SMB ?") == "rag"


def test_rag_top_product_definition_variant():
    assert route_question("Comment est defini un top product ?") == "rag"


def test_rag_country_meaning_variant():
    assert route_question("A quoi correspond le pays dans les analyses ?") == "rag"
