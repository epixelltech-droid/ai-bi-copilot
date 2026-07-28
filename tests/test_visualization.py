from app.visualization.plotly_builder import build_visualization


def test_builds_bar_chart_for_revenue_by_country():
    rows = [
        {"country": "France", "revenue": 100.0},
        {"country": "Maroc", "revenue": 200.0},
    ]

    visualization = build_visualization("Quel est le chiffre d'affaires par pays ?", rows)

    assert visualization["enabled"] is True
    assert visualization["kind"] == "bar"
    assert visualization["figure"]["data"][0]["type"] == "bar"
    assert visualization["figure"]["data"][0]["x"] == ["Maroc", "France"]
    assert visualization["figure"]["data"][0]["y"] == [200.0, 100.0]


def test_builds_line_chart_for_monthly_revenue():
    rows = [
        {"month_name": "janvier", "revenue": 100.0},
        {"month_name": "fevrier", "revenue": 150.0},
    ]

    visualization = build_visualization("Quel est le chiffre d'affaires par mois ?", rows)

    assert visualization["enabled"] is True
    assert visualization["kind"] == "line"
    assert visualization["figure"]["data"][0]["type"] == "scatter"
    assert visualization["figure"]["data"][0]["mode"] == "lines+markers"


def test_does_not_build_chart_for_empty_or_unshaped_rows():
    assert build_visualization("Question", [])["enabled"] is False
    assert build_visualization("Question", [{"revenue": 100.0}])["enabled"] is False
    assert build_visualization("Question", [{"country": "France"}])["enabled"] is False
