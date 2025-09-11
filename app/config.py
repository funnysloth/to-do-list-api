from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_MINUTES: int
    REFRESH_TOKEN_EXPIRATION_DAYS: int
    REFRESH_TOKEN_SECRET: str

settings = Settings() # type: ignore