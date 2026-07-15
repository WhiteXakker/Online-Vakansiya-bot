from functools import lru_cache
from typing import Annotated, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    admin_ids: Annotated[List[int], NoDecode] = Field(default_factory=list, alias="ADMIN_IDS")
    channel_id: str = Field(default="@UstozShogird", alias="CHANNEL_ID")
    moderation_chat_id: int | None = Field(default=None, alias="MODERATION_CHAT_ID")

    @field_validator("moderation_chat_id", mode="before")
    @classmethod
    def parse_moderation_chat_id(cls, value: str | int | None) -> int | None:
        if value is None or value == "":
            return None
        return int(value)
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/bot.db",
        alias="DATABASE_URL",
    )
    fsm_storage: str = Field(default="memory", alias="FSM_STORAGE")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    broadcast_delay: float = Field(default=0.05, alias="BROADCAST_DELAY")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: str | List[int]) -> List[int]:
        if isinstance(value, list):
            return [int(item) for item in value]
        if not value:
            return []
        return [int(item.strip()) for item in str(value).split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
