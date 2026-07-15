import time
from typing import TYPE_CHECKING

from config.settings import settings
from database import queries

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

_CACHE_TTL_SECONDS = 60.0
_admin_cache: dict[int, tuple[bool, float]] = {}


def invalidate_admin_cache(telegram_id: int | None = None) -> None:
    if telegram_id is None:
        _admin_cache.clear()
        return
    _admin_cache.pop(telegram_id, None)


def is_env_super_admin(telegram_id: int) -> bool:
    return telegram_id in settings.admin_ids


async def is_admin(session: "AsyncSession", telegram_id: int) -> bool:
    if is_env_super_admin(telegram_id):
        return True

    now = time.monotonic()
    cached = _admin_cache.get(telegram_id)
    if cached and now - cached[1] < _CACHE_TTL_SECONDS:
        return cached[0]

    is_db_admin = await queries.user_has_admin_flag(session, telegram_id)
    _admin_cache[telegram_id] = (is_db_admin, now)
    return is_db_admin
