from pathlib import Path


def test_knowledge_base_files_exist_and_are_not_empty():
    base_dir = Path("knowledge_base")

    assert base_dir.exists()
    assert base_dir.is_dir()

    expected_files = [
        base_dir / "kpi_dictionary.md",
        base_dir / "data_dictionary.md",
        base_dir / "business_rules.md",
    ]

    for file_path in expected_files:
        assert file_path.exists()
        assert file_path.is_file()
        assert file_path.read_text(encoding="utf-8").strip()


def test_kpi_dictionary_contains_main_kpis():
    content = Path("knowledge_base/kpi_dictionary.md").read_text(encoding="utf-8")

    assert "Revenue" in content
    assert "Margin" in content
    assert "Margin %" in content
    assert "Gross Margin" in content
    assert "Average Selling Price" in content
    assert "ASP" in content


def test_data_dictionary_contains_star_schema_tables():
    content = Path("knowledge_base/data_dictionary.md").read_text(encoding="utf-8")

    assert "fact_sales" in content
    assert "dim_customer" in content
    assert "dim_product" in content
    assert "dim_date" in content
    assert "SMB" in content
    assert "Retail" in content
    assert "Enterprise" in content
    assert "Country always comes from" in content
    assert "Category is used to group products" in content


def test_business_rules_contains_revenue_and_non_hallucination_rules():
    content = Path("knowledge_base/business_rules.md").read_text(encoding="utf-8")

    assert "Revenue" in content
    assert "must never invent" in content
    assert "must not invent a cause" in content
    assert "Average Selling Price" in content
    assert "Gross Margin" in content
    assert "top product by quantity" in content
