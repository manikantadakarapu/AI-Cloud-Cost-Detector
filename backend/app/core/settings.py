from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Cost Detective API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "local"
    log_level: str = "INFO"

    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    analysis_queue_name: str = "analysis"

    azure_tenant_id: str | None = Field(default=None, alias="AZURE_TENANT_ID")
    azure_client_id: str | None = Field(default=None, alias="AZURE_CLIENT_ID")
    azure_client_secret: str | None = Field(default=None, alias="AZURE_CLIENT_SECRET")
    azure_openapi_client_id: str | None = Field(default=None, alias="AZURE_OPENAPI_CLIENT_ID")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        return str(self.database_url)

    @property
    def has_service_principal_config(self) -> bool:
        return all(
            [
                self.azure_tenant_id,
                self.azure_client_id,
                self.azure_client_secret,
            ]
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
