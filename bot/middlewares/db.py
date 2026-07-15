from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import async_session_factory
from database import queries


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with async_session_factory() as session:
            data["session"] = session
            return await handler(event, data)


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from aiogram.types import CallbackQuery, Message

        user = None
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user

        if user:
            session: AsyncSession = data["session"]
            if await queries.is_user_banned(session, user.id):
                if isinstance(event, Message):
                    await event.answer("🚫 Siz botdan foydalanish huquqidan mahrum qilgansiz.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("🚫 Siz botdan foydalanish huquqidan mahrum qilgansiz.", show_alert=True)
                return None

        return await handler(event, data)
