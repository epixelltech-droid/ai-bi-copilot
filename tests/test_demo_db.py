import sqlite3


def connect_db():
    conn = sqlite3.connect("data/demo.db")
    conn.row_factory = sqlite3.Row
    return conn


def test_star_schema_tables_exist():
    with connect_db() as conn:
        rows = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN ('dim_customer', 'dim_product', 'dim_date', 'fact_sales')
            ORDER BY name
            """
        ).fetchall()

    assert [row["name"] for row in rows] == ["dim_customer", "dim_date", "dim_product", "fact_sales"]


def test_star_schema_contains_data():
    with connect_db() as conn:
        counts = {
            "dim_customer": conn.execute("SELECT COUNT(*) FROM dim_customer").fetchone()[0],
            "dim_product": conn.execute("SELECT COUNT(*) FROM dim_product").fetchone()[0],
            "dim_date": conn.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0],
            "fact_sales": conn.execute("SELECT COUNT(*) FROM fact_sales").fetchone()[0],
        }

    assert counts["dim_customer"] == 50
    assert counts["dim_product"] == 18
    assert counts["dim_date"] == 730
    assert counts["fact_sales"] == 3000


def test_fact_sales_foreign_keys_are_valid():
    with connect_db() as conn:
        invalid_rows = conn.execute(
            """
            SELECT COUNT(*)
            FROM fact_sales f
            LEFT JOIN dim_date d ON d.date_id = f.date_id
            LEFT JOIN dim_customer c ON c.customer_id = f.customer_id
            LEFT JOIN dim_product p ON p.product_id = f.product_id
            WHERE d.date_id IS NULL
               OR c.customer_id IS NULL
               OR p.product_id IS NULL
            """
        ).fetchone()[0]

    assert invalid_rows == 0


def test_revenue_matches_quantity_times_unit_price():
    with connect_db() as conn:
        mismatches = conn.execute(
            """
            SELECT COUNT(*)
            FROM (
                SELECT quantity, unit_price, revenue
                FROM fact_sales
                ORDER BY sale_id
                LIMIT 25
            )
            WHERE ABS(revenue - ROUND(quantity * unit_price, 2)) > 0.001
            """
        ).fetchone()[0]

    assert mismatches == 0


def test_margin_matches_revenue_minus_cost():
    with connect_db() as conn:
        mismatches = conn.execute(
            """
            SELECT COUNT(*)
            FROM fact_sales
            WHERE ABS(margin - ROUND(revenue - cost, 2)) > 0.001
            """
        ).fetchone()[0]

    assert mismatches == 0
