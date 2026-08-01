from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    demo_mode: bool = True
    sqlite_path: str = "data/demo.db"
    max_rows: int = 200

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    hybrid_llm_enabled: bool = False

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""

    sqlserver_connection_string: str = ""
    powerbi_dataset_id: str = ""
    powerbi_access_token: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
