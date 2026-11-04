from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    auth_service_url: str = "http://localhost:8001"
    accounts_service_url: str = "http://localhost:8002"
    planner_data_service_url: str = "http://localhost:8003"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
