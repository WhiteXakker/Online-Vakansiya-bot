import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import admin_panel_keyboard, broadcast_confirm_keyboard
from bot.states.admin import BroadcastState
from config.settings import settings
from database import queries

router = Router(name="admin_broadcast")


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.callback_query(F.data == "admin:broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return

    await state.set_state(BroadcastState.waiting_content)
    await callback.message.edit_text(
        "📢 <b>Broadcast</b>\n\n"
        "Yuboriladigan xabarni yuboring (matn, rasm, video yoki hujjat).\n"
        "Bekor qilish: /cancel",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(BroadcastState.waiting_content, F.text == "/cancel")
async def cancel_broadcast(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Broadcast bekor qilindi.", reply_markup=admin_panel_keyboard())


@router.message(BroadcastState.waiting_content)
async def receive_broadcast_content(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    await state.update_data(
        broadcast_chat_id=message.chat.id,
        broadcast_message_id=message.message_id,
    )
    await state.set_state(BroadcastState.confirm)
    await message.answer(
        "Xabar yuqoridagi ko'rinishda yuboriladi.\nTasdiqlaysizmi?",
        reply_markup=broadcast_confirm_keyboard(),
    )


@router.callback_query(F.data == "admin:broadcast:cancel")
async def cancel_broadcast_callback(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "Broadcast bekor qilindi.",
        reply_markup=admin_panel_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast:send")
async def send_broadcast(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return

    data = await state.get_data()
    source_chat_id = data.get("broadcast_chat_id")
    source_message_id = data.get("broadcast_message_id")
    if not source_chat_id or not source_message_id:
        await callback.answer("Xabar topilmadi.", show_alert=True)
        await state.clear()
        return

    user_ids = await queries.get_all_user_telegram_ids(session)
    total = len(user_ids)
    if total == 0:
        await callback.message.edit_text("Foydalanuvchilar topilmadi.")
        await state.clear()
        return

    sent = 0
    failed = 0
    progress_message = await callback.message.edit_text(f"📤 Yuborilmoqda... 0/{total}")

    for index, user_id in enumerate(user_ids, start=1):
        try:
            await callback.bot.copy_message(
                chat_id=user_id,
                from_chat_id=source_chat_id,
                message_id=source_message_id,
            )
            sent += 1
        except Exception:
            failed += 1

        if index % 25 == 0 or index == total:
            percent = int(index / total * 100)
            bar_filled = percent // 5
            bar = "█" * bar_filled + "░" * (20 - bar_filled)
            await progress_message.edit_text(
                f"📤 Broadcast jarayoni\n"
                f"[{bar}] {percent}%\n"
                f"✅ Yuborildi: {sent} | ❌ Xato: {failed} | Jami: {total}"
            )

        await asyncio.sleep(settings.broadcast_delay)

    await progress_message.edit_text(
        f"✅ Broadcast yakunlandi!\n\n"
        f"Yuborildi: {sent}\n"
        f"Xato: {failed}\n"
        f"Jami: {total}",
        reply_markup=admin_panel_keyboard(),
    )
    await state.clear()
    await callback.answer()
