from functools import lru_cache
from typing import Literal
from pathlib import Path
import os

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = Path(os.getenv("ENV_FILE", PROJECT_ROOT / "deployment" / "local" / ".env"))


class _Base(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DatabaseSetting(_Base):
    DATABASE_URL: str


class RedisSetting(_Base):
    REDIS_HOST: str
    REDIS_PORT: int = Field(ge=1, le=65535)
    REDIS_CACHE_TTL_SECONDS: int = 86400


class RabbitMqSetting(_Base):
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = Field(ge=1, le=65535)
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    RABBITMQ_EXCHANGE: str
    RABBITMQ_QUEUE: str
    RABBITMQ_ROUTING_KEY: str


class APISetting(_Base):
    BASE_URL: str
    SECRET_KEY: SecretStr
    JWT_ALGORITHM: Literal["HS256", "HS384", "HS512"] = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


class GeoIpSetting(_Base):
    GEOLITE2_PATH: str


class FrontendSetting(_Base):
    FRONTEND_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.FRONTEND_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_database_setting() -> DatabaseSetting:
    return DatabaseSetting()

@lru_cache
def get_geoip_setting() -> GeoIpSetting:
    return GeoIpSetting()

@lru_cache
def get_redis_setting() -> RedisSetting:
    return RedisSetting()

@lru_cache
def get_rabbitmq_setting() -> RabbitMqSetting:
    return RabbitMqSetting()

@lru_cache
def get_api_setting() -> APISetting:
    return APISetting()

@lru_cache
def get_frontend_setting() -> FrontendSetting:
    return FrontendSetting()