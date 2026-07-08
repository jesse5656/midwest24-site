from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://archive:archive_dev_password@archive-db:5432/archive"

    document_storage_root: str = "storage/documents"

    embedding_provider: str = "mock"
    embedding_model: str = "mock"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
