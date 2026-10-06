from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL:str
    BASE_URL:str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_HOST:str
    REDIS_PORT:int
    REDIS_CACHE_TTL_SECONDS: int = 86400
    GEOLITE2_PATH:str
    FRONTEND_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"

    RABBITMQ_HOST:str
    RABBITMQ_USER:str
    RABBITMQ_PORT:int
    RABBITMQ_PASS:str
    RABBITMQ_EXCHANGE:str
    RABBITMQ_QUEUE:str
    RABBITMQ_ROUTING_KEY:str


    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings=Settings()
