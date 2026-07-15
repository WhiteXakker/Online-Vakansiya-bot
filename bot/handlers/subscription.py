from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import main_menu_keyboard
from bot.utils.subscription import (
    SUBSCRIPTION_CHECK_CALLBACK,
    build_subscription_message,
    get_unsubscribed_channels,
    subscription_keyboard,
)
from database import queries

router = Router(name="subscription")


@router.callback_query(F.data == SUBSCRIPTION_CHECK_CALLBACK)
async def check_subscription(callback: CallbackQuery, session: AsyncSession) -> None:
    await queries.get_or_create_user(
        session,
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )

    missing = await get_unsubscribed_channels(callback.bot, session, callback.from_user.id)
    if missing:
        text = build_subscription_message(missing)
        await callback.message.edit_text(
            text,
            reply_markup=subscription_keyboard(missing),
            parse_mode="HTML",
        )
        await callback.answer("Hali barcha kanallarga a'zo emassiz.", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ <b>Obuna tasdiqlandi!</b>\n\nEndi botdan to'liq foydalanishingiz mumkin.",
        parse_mode="HTML",
    )
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer("Obuna muvaffaqiyatli tasdiqlandi!")
