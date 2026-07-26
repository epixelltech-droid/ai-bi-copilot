import httpx
from app.core.config import get_settings

def execute_dax(query: str) -> list[dict]:
    s = get_settings()
    if not s.powerbi_dataset_id or not s.powerbi_access_token:
        raise RuntimeError("Power BI credentials are not configured.")

    url = f"https://api.powerbi.com/v1.0/myorg/datasets/{s.powerbi_dataset_id}/executeQueries"
    headers = {
        "Authorization": f"Bearer {s.powerbi_access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "queries": [{"query": query}],
        "serializerSettings": {"includeNulls": True},
    }
    with httpx.Client(timeout=60) as client:
        r = client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        body = r.json()

    tables = body.get("results", [{}])[0].get("tables", [])
    return tables[0].get("rows", []) if tables else []
