import app.agents.router as router


def test_llm_route_can_override_auto_mode(monkeypatch):
    monkeypatch.setattr(
        router,
        "llm_json",
        lambda *args, **kwargs: {
            "route": "rag",
            "rewritten_question": "Que signifie Revenue ?",
            "reason": "definition request",
        },
    )

    analysis = router.analyze_question("revenue stp")

    assert analysis["route"] == "rag"
    assert analysis["rewritten_question"] == "Que signifie Revenue ?"


def test_llm_route_is_ignored_when_invalid(monkeypatch):
    monkeypatch.setattr(
        router,
        "llm_json",
        lambda *args, **kwargs: {
            "route": "unknown",
            "rewritten_question": "bad",
        },
    )

    analysis = router.analyze_question("Quel est le CA par pays ?")

    assert analysis["route"] == "sql"
    assert analysis["rewritten_question"] == "Quel est le CA par pays ?"


def test_sql():
    assert router.route_question("Quel est le CA par pays ?") == "sql"


def test_powerbi():
    assert router.route_question("Genere une requete DAX Power BI") == "powerbi"


def test_rag():
    assert router.route_question("Quelle est la definition de la marge ?") == "rag"


def test_rag_enterprise_definition():
    assert router.route_question("Qu'est-ce qu'un client Enterprise ?") == "rag"


def test_rag_difference_question():
    assert router.route_question("Quelle est la difference entre Revenue et Margin ?") == "rag"


def test_sql_short_revenue_variant():
    assert router.route_question("CA par pays") == "sql"


def test_sql_monthly_revenue_variant():
    assert router.route_question("revenu mensuel") == "sql"


def test_rag_definition_margin_variant():
    assert router.route_question("definition de margin") == "rag"


def test_rag_c_est_quoi_revenue_variant():
    assert router.route_question("c'est quoi revenue") == "rag"


def test_rag_que_veut_dire_smb_variant():
    assert router.route_question("Que veut dire SMB ?") == "rag"


def test_rag_top_product_definition_variant():
    assert router.route_question("Comment est defini un top product ?") == "rag"


def test_rag_country_meaning_variant():
    assert router.route_question("A quoi correspond le pays dans les analyses ?") == "rag"


def test_short_revenue_term_routes_to_rag():
    assert router.route_question("Revenue ?") == "rag"


def test_short_margin_percent_term_routes_to_rag():
    assert router.route_question("Margin %") == "rag"


def test_compare_countries_revenue_routes_to_sql():
    assert router.route_question("Compare le chiffre d'affaires entre la France et le Maroc") == "sql"


def test_difference_between_countries_revenue_routes_to_sql():
    assert router.route_question("Quelle est la difference de chiffre d'affaires entre la France et le Maroc ?") == "sql"


def test_enterprise_top_customers_routes_to_sql():
    assert router.route_question("Quels sont les clients Enterprise les plus performants ?") == "sql"


def test_business_rules_question_routes_to_rag():
    assert router.route_question("Quelles sont les regles metier de la marge ?") == "rag"


def test_january_2026_sales_question_routes_to_sql():
    assert router.route_question("Affiche les ventes de janvier 2026") == "sql"
