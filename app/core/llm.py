import json

from openai import OpenAI

from app.core.config import get_settings


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()


def get_llm_client() -> tuple[OpenAI, str] | None:
    settings = get_settings()

    if not settings.hybrid_llm_enabled:
        return None

    if settings.openai_api_key and settings.openai_model:
        return OpenAI(api_key=settings.openai_api_key), settings.openai_model

    if (
        settings.azure_openai_endpoint
        and settings.azure_openai_api_key
        and settings.azure_openai_deployment
    ):
        client = OpenAI(
            api_key=settings.azure_openai_api_key,
            base_url=f"{settings.azure_openai_endpoint.rstrip('/')}/openai/v1/",
        )
        return client, settings.azure_openai_deployment

    return None


def get_llm_runtime_info() -> dict[str, str | bool]:
    settings = get_settings()
    if settings.openai_api_key and settings.openai_model:
        return {
            "provider": "openai",
            "model": settings.openai_model,
            "configured": True,
            "enabled": settings.hybrid_llm_enabled,
        }

    if (
        settings.azure_openai_endpoint
        and settings.azure_openai_api_key
        and settings.azure_openai_deployment
    ):
        return {
            "provider": "azure_openai",
            "model": settings.azure_openai_deployment,
            "configured": True,
            "enabled": settings.hybrid_llm_enabled,
        }

    return {
        "provider": "none",
        "model": "",
        "configured": False,
        "enabled": settings.hybrid_llm_enabled,
    }


def llm_text(system: str, user: str) -> str | None:
    client_config = get_llm_client()
    if client_config is None:
        return None

    client, model = client_config
    response = client.responses.create(
        model=model,
        instructions=system,
        input=user,
    )
    return response.output_text


def llm_json(system: str, user: str) -> dict | None:
    result = llm_text(system, user)
    if not result:
        return None

    try:
        payload = json.loads(_strip_code_fences(result))
    except json.JSONDecodeError:
        return None

    return payload if isinstance(payload, dict) else None
