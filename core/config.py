from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL:str
    BASE_URL:str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_HOST:str
    REDIS_PORT:int

    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings=Settings()
