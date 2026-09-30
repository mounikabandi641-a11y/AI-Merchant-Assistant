from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Merchant Assistant"
    environment: str = "development"
    sqlite_database_url: str = "sqlite:///./merchant_assistant.db"

    class Config:
        env_file = ".env"


settings = Settings()
