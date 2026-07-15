from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import (
    admin_panel_keyboard, 
    mandatory_channels_keyboard
)
from bot.states.admin import AdminPanel
from database import queries

router = Router(name="admin_panel")


@router.message(Command("admin"))
async def cmd_admin(message: Message, session: AsyncSession) -> None:
    # Dinamik tarzda bazadan tekshiradi
    if not await queries.is_user_admin(session, message.from_user.id):
        await message.answer("⛔ Sizda admin huquqi yo'q.")
        return

    await message.answer(
        "🛠 <b>Admin Panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin:close")
async def close_admin_panel(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return

    stats = await queries.get_stats(session)
    channel_id = await queries.get_channel_id(session)
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"🟢 Faol (7 kun): <b>{stats['active_users']}</b>\n"
        f"🚫 Ban qilingan: <b>{stats['banned_users']}</b>\n"
        f"📝 Jami arizalar: <b>{stats['total_submissions']}</b>\n"
        f"⏳ Kutilayotgan: <b>{stats['pending_posts']}</b>\n"
        f"✅ Joylangan: <b>{stats['total_posted']}</b>\n\n"
        f"📢 Kanal: <code>{channel_id}</code>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin:back")
async def back_to_admin_panel(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    await callback.message.edit_text(
        "🛠 <b>Admin Panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


# ================= 📌 MAJBURIY OBUNA BOSHQARUVI =================

@router.callback_query(F.data == "admin:mandatory")
async def show_channels_menu(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    channels = await queries.get_all_channels(session)
    await callback.message.edit_text(
        "📌 <b>Majburiy obuna kanallari:</b>\n\n"
        "O'chirmoqchi bo'lgan kanal ustidagi 🗑 belgisini bosing.",
        reply_markup=mandatory_channels_keyboard(channels),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:mandatory:add")
async def start_add_channel(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    await state.set_state(AdminPanel.waiting_channel_id)
    await callback.message.edit_text(
        "✏️ Kanalning Telegram ID sini kiriting (masalan: <code>-1001234567890</code>):\n\n"
        "Yoki @username ko'rinishida yuboring.\n"
        "Bekor qilish uchun: /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


# Kanal ID si qabul qilingandan so'ng, nomini so'raymiz
@router.message(AdminPanel.waiting_channel_id, F.text != "/cancel")
async def process_channel_id(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return
    
    # Agar biz kanal sozlamalaridagi eski tizim bilan to'qnashmasligimiz kerak bo'lsa,
    # Majburiy obunaga qo'shish ekanini tekshirib olish uchun State-ga belgi qo'yamiz.
    await state.update_data(new_m_channel_id=message.text.strip())
    await state.set_state(AdminPanel.waiting_channel_name) # start.py yoki FSM dagi mos state
    await message.answer("✏️ Kanal nomini kiriting (Tugmada chiqadigan qisqa matn):")


@router.message(AdminPanel.waiting_channel_name, F.text != "/cancel")
async def process_channel_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return
    await state.update_data(new_m_channel_name=message.text.strip())
    await state.set_state(AdminPanel.waiting_channel_link)
    await message.answer("✏️ Kanal taklif havolasini (invite link) yuboring:")


@router.message(AdminPanel.waiting_channel_link, F.text != "/cancel")
async def process_channel_link(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return
    data = await state.get_data()
    
    # Bazaga yozamiz
    await queries.add_mandatory_channel(
        session,
        channel_id=data['new_m_channel_id'],
        name=data['new_m_channel_name'],
        invite_link=message.text.strip()
    )
    await state.clear()
    await message.answer(
        "✅ Kanal majburiy obunaga muvaffaqiyatli qo'shildi!",
        reply_markup=admin_panel_keyboard()
    )


@router.callback_query(F.data.startswith("admin:mandatory:del:"))
async def delete_channel_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    channel_db_id = int(callback.data.split(":")[-1])
    await queries.delete_mandatory_channel(session, channel_db_id)
    channels = await queries.get_all_channels(session)
    await callback.message.edit_text(
        "✅ Kanal o'chirildi!\n📌 <b>Yangi ro'yxat:</b>",
        reply_markup=mandatory_channels_keyboard(channels),
        parse_mode="HTML"
    )
    await callback.answer()