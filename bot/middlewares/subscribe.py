# bot/middlewares/subscribe.py

from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from database import queries

class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # 1. Faqat Message va CallbackQuery hodisalarini tekshiramiz
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        session: AsyncSession = data.get("session")
        bot = data.get("bot")

        # Adminlar uchun majburiy obuna tekshiruvini o'tkazib yuboramiz
        if await queries.is_user_admin(session, user_id):
            return await handler(event, data)

        # Hamma majburiy kanallarni bazadan olamiz
        channels = await queries.get_all_channels(session)
        if not channels:
            return await handler(event, data)

        not_subscribed_channels = []

        # Har bir kanalga a'zolikni tekshiramiz
        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=str(channel.channel_id), user_id=user_id)
                if member.status in ["left", "kicked"]:
                    not_subscribed_channels.append(channel)
            except Exception:
                not_subscribed_channels.append(channel)

        # AGAR FOYDALANUVChI HAMMA KANALGA OBUNA BO'LMAGAN BO'LSA
        if not_subscribed_channels:
            buttons = []
            for ch in not_subscribed_channels:
                buttons.append([InlineKeyboardButton(text=f"📢 {ch.channel_name}", url=ch.invite_link)])
            
            buttons.append([InlineKeyboardButton(text="🔄 Obunani tekshirish", callback_data="check_subscription")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

            warning_text = (
                "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz shart!</b>\n\n"
                "Iltimos, barcha kanallarga a'zo bo'lib, keyin 'Obunani tekshirish' tugmasini bosing."
            )

            if isinstance(event, Message):
                await event.answer(warning_text, reply_markup=keyboard, parse_mode="HTML")
                
            elif isinstance(event, CallbackQuery):
                if event.data == "check_subscription":
                    # Hali ham a'zo bo'lmagani uchun chiroyli oyna (Alert) chiqariladi
                    await event.answer("❌ Hali ham ba'zi kanallarga obuna bo'lmadingiz!", show_alert=True)
                else:
                    await event.message.answer(warning_text, reply_markup=keyboard, parse_mode="HTML")
                    await event.answer()
            
            return  # Jarayonni to'xtatamiz, handlerga o'tishga yo'l qo'ymaymiz

        # -------------------------------------------------------------
        # AGAR FOYDALANUVChI HAMMA KANALGA OBUNA BO'LGAN BO'LSA VA TUGMANI BOSSA:
        # -------------------------------------------------------------
        if isinstance(event, CallbackQuery) and event.data == "check_subscription":
            try:
                # Obuna bo'ling degan xabarni chiroyli qilib o'chiramiz
                await event.message.delete()
            except Exception:
                pass
                
            await event.message.answer(
                "🎉 <b>Tabriklaymiz!</b>\n\nSiz barcha kanallarga muvaffaqiyatli a'zo bo'ldingiz! "
                "Botdan bemalol foydalanishingiz mumkin. Boshlash uchun /start bosing.",
                parse_mode="HTML"
            )
            await event.answer() # Telegram yuklanish belgisini to'xtatish uchun
            return  # Routerga uzatib o'tirmaymiz, ish tugadi!

        # Qolgan barcha holatlarda so'rovni oddiy handlerlarga o'tkazamiz
        return await handler(event, data)