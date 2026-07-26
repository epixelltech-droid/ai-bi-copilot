from app.connectors.schema_metadata import (
    format_schema_for_llm,
    get_columns,
    get_foreign_keys,
    get_relations,
    get_schema_metadata,
    get_tables,
)


def test_business_tables_are_detected():
    assert get_tables() == ["dim_customer", "dim_product", "dim_date", "fact_sales"]


def test_fact_sales_columns_are_detected():
    columns = get_columns("fact_sales")
    column_names = [column["name"] for column in columns]

    assert column_names == [
        "sale_id",
        "date_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price",
        "revenue",
        "cost",
        "margin",
    ]


def test_dim_customer_primary_key_is_detected():
    metadata = get_schema_metadata()

    assert metadata["dim_customer"]["primary_key"] == ["customer_id"]


def test_fact_sales_foreign_keys_are_detected():
    foreign_keys = get_foreign_keys("fact_sales")

    assert len(foreign_keys) == 3
    assert {"from": "date_id", "to_table": "dim_date", "to_column": "date_id"} in foreign_keys
    assert {"from": "customer_id", "to_table": "dim_customer", "to_column": "customer_id"} in foreign_keys
    assert {"from": "product_id", "to_table": "dim_product", "to_column": "product_id"} in foreign_keys


def test_relations_point_to_dimensions():
    relations = get_relations()

    assert {
        "from_table": "fact_sales",
        "from_column": "customer_id",
        "to_table": "dim_customer",
        "to_column": "customer_id",
    } in relations
    assert {
        "from_table": "fact_sales",
        "from_column": "product_id",
        "to_table": "dim_product",
        "to_column": "product_id",
    } in relations
    assert {
        "from_table": "fact_sales",
        "from_column": "date_id",
        "to_table": "dim_date",
        "to_column": "date_id",
    } in relations


def test_format_schema_for_llm_contains_main_tables_and_relations():
    formatted_schema = format_schema_for_llm()

    assert "TABLE fact_sales" in formatted_schema
    assert "TABLE dim_customer" in formatted_schema
    assert "TABLE dim_product" in formatted_schema
    assert "TABLE dim_date" in formatted_schema
    assert "fact_sales.customer_id -> dim_customer.customer_id" in formatted_schema
    assert "fact_sales.product_id -> dim_product.product_id" in formatted_schema
    assert "fact_sales.date_id -> dim_date.date_id" in formatted_schema
