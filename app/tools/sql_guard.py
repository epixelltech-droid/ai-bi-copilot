import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|merge|exec|execute|grant|revoke|create)\b",
    re.IGNORECASE,
)

def validate_readonly_sql(query: str) -> str:
    clean = query.strip().rstrip(";")
    if FORBIDDEN.search(clean):
        raise ValueError("Unsafe SQL statement blocked.")
    if not re.match(r"^(select|with)\b", clean, re.IGNORECASE):
        raise ValueError("Only SELECT/CTE queries are allowed.")
    if ";" in clean:
        raise ValueError("Multiple SQL statements are not allowed.")
    return clean
