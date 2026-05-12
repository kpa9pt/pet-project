from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_token: str
    database_url: str
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def get_settings():
    return Settings()
