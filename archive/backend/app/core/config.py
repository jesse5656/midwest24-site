from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://archive:archive_dev_password@archive-db:5432/archive"

    class Config:
        env_file = ".env"


settings = Settings()
