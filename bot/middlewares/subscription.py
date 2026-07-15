# bot/handlers/subscription.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

# Router nomi qat'iy ravishda "router" bo'lishi kerak:
router = Router(name="subscription")

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery, session: AsyncSession):
    try:
        await callback.message.delete()
    except Exception:
        pass
        
    await callback.message.answer(
        "🎉 <b>Tabriklaymiz!</b>\n\nSiz barcha kanallarga muvaffaqiyatli a'zo bo'ldingiz! "
        "Botdan bemalol foydalanishingiz mumkin. Menyu ochish uchun /start bosing.",
        parse_mode="HTML"
    )
    await callback.answer()