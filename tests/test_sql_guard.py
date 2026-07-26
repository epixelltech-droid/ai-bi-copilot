import pytest
from app.tools.sql_guard import validate_readonly_sql

def test_select_allowed():
    assert validate_readonly_sql("SELECT * FROM fact_sales") == "SELECT * FROM fact_sales"

@pytest.mark.parametrize("query", [
    "DELETE FROM fact_sales",
    "DROP TABLE fact_sales",
    "UPDATE fact_sales SET revenue=0",
    "INSERT INTO fact_sales VALUES (1)",
])
def test_unsafe_blocked(query):
    with pytest.raises(ValueError):
        validate_readonly_sql(query)
