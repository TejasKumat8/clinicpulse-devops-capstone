from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration read from environment variables (12-Factor App design)."""

    app_name: str = "ClinicPulse API"
    database_url: str = "postgresql+psycopg://clinicpulse:clinicpulse_secret@localhost:5432/clinicpulse"
    clinic_timezone: str = "Asia/Kolkata"
    git_sha: str = "local"
    environment: str = "development"
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
