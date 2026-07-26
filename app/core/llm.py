from openai import OpenAI
from app.core.config import get_settings

def get_azure_openai_client() -> OpenAI | None:
    s = get_settings()
    if not (s.azure_openai_endpoint and s.azure_openai_api_key and s.azure_openai_deployment):
        return None
    return OpenAI(
        api_key=s.azure_openai_api_key,
        base_url=f"{s.azure_openai_endpoint.rstrip('/')}/openai/v1/",
    )

def llm_text(system: str, user: str) -> str | None:
    s = get_settings()
    client = get_azure_openai_client()
    if client is None:
        return None
    response = client.responses.create(
        model=s.azure_openai_deployment,
        instructions=system,
        input=user,
    )
    return response.output_text
