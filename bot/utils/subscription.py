import logging
from html import escape

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MandatoryChannel
from database import queries

logger = logging.getLogger(__name__)

SUBSCRIPTION_CHECK_CALLBACK = "sub:check"

_MEMBER_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


async def _is_subscribed_to_channel(bot: Bot, channel_id: str, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in _MEMBER_STATUSES
    except Exception as exc:
        logger.warning("Subscription check failed for channel %s: %s", channel_id, exc)
        return False


async def get_unsubscribed_channels(
    bot: Bot,
    session: AsyncSession,
    user_id: int,
) -> list[MandatoryChannel]:
    channels = await queries.get_mandatory_channels(session)
    if not channels:
        return []

    missing: list[MandatoryChannel] = []
    for channel in channels:
        if not await _is_subscribed_to_channel(bot, channel.channel_id, user_id):
            missing.append(channel)
    return missing


def build_subscription_message(channels: list[MandatoryChannel]) -> str:
    lines = [
        "📢 <b>Majburiy obuna</b>",
        "",
        "Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:",
        "",
    ]
    for index, channel in enumerate(channels, start=1):
        name = escape(channel.channel_name)
        lines.append(f"{index}. <b>{name}</b>")
    lines.extend(["", "A'zo bo'lgach, <b>🔄 Tekshirish</b> tugmasini bosing."])
    return "\n".join(lines)


def subscription_keyboard(channels: list[MandatoryChannel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for channel in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"📢 {channel.channel_name}",
                url=channel.invite_link,
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔄 Tekshirish", callback_data=SUBSCRIPTION_CHECK_CALLBACK)
    )
    return builder.as_markup()
