from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers import router as main_router
from bot.middlewares.db import BanCheckMiddleware, DatabaseMiddleware
from bot.middlewares.subscribe import SubscriptionCheckMiddleware
from config.settings import settings


def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    if settings.fsm_storage.lower() == "redis":
        from aiogram.fsm.storage.redis import RedisStorage
        from redis.asyncio import Redis

        redis = Redis.from_url(settings.redis_url)
        storage = RedisStorage(redis=redis)
    else:
        storage = MemoryStorage()

    dp = Dispatcher(storage=storage)
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(BanCheckMiddleware())
    dp.message.outer_middleware(SubscriptionCheckMiddleware())
    dp.callback_query.outer_middleware(SubscriptionCheckMiddleware())
    dp.include_router(main_router)
    return dp
