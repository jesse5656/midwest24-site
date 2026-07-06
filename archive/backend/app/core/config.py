from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://archive:archive_dev_password@archive-db:5432/archive"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
