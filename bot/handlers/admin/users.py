from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import (
    admin_panel_keyboard, 
    user_management_keyboard,
    admins_list_keyboard
)
from bot.states.admin import AdminPanel
from config.settings import settings
from database import queries

router = Router(name="admin_users")


@router.callback_query(F.data == "admin:users")
async def users_menu(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return

    await state.set_state(AdminPanel.waiting_user_search)
    await callback.message.edit_text(
        "👥 <b>Foydalanuvchi qidirish</b>\n\n"
        "Telegram ID yoki @username yuboring.\n"
        "Orqaga: /cancel",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminPanel.waiting_user_search, F.text == "/cancel")
async def cancel_user_search(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return
    await state.clear()
    await message.answer("Admin panel.", reply_markup=admin_panel_keyboard())


@router.message(AdminPanel.waiting_user_search, F.text)
async def search_user(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return

    user = await queries.find_user(session, message.text.strip())
    if not user:
        await message.answer("Foydalanuvchi topilmadi. Qayta urinib ko'ring yoki /cancel")
        return

    status = "🚫 Ban qilingan" if user.is_banned else "✅ Faol"
    
    # Ushbu user admin yoki yo'qligini tekshiramiz
    is_user_adm = await queries.is_user_admin(session, user.telegram_id)
    is_super = user.telegram_id in settings.admin_ids

    await message.answer(
        f"👤 <b>Foydalanuvchi</b>\n\n"
        f"ID: <code>{user.telegram_id}</code>\n"
        f"Username: @{user.username or 'yoq'}\n"
        f"Ism: {user.full_name or '—'}\n"
        f"Holat: {status}\n"
        f"Ro'yxatdan o'tgan: {user.created_at:%Y-%m-%d %H:%M}",
        reply_markup=user_management_keyboard(
            user.telegram_id, 
            user.is_banned,
            is_admin=is_user_adm,
            is_super_admin=is_super
        ),
        parse_mode="HTML",
    )
    await state.clear()


@router.callback_query(F.data.startswith("admin:ban:"))
async def ban_user(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return

    telegram_id = int(callback.data.split(":")[-1])
    user = await queries.set_user_ban(session, telegram_id, banned=True)
    if not user:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    is_user_adm = await queries.is_user_admin(session, user.telegram_id)
    is_super = user.telegram_id in settings.admin_ids

    await callback.message.edit_reply_markup(
        reply_markup=user_management_keyboard(
            user.telegram_id, 
            user.is_banned,
            is_admin=is_user_adm,
            is_super_admin=is_super
        )
    )
    await callback.answer("Foydalanuvchi ban qilindi.")


@router.callback_query(F.data.startswith("admin:unban:"))
async def unban_user(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return

    telegram_id = int(callback.data.split(":")[-1])
    user = await queries.set_user_ban(session, telegram_id, banned=False)
    if not user:
        await callback.answer("Foydalanuvchi topilmadi.", show_alert=True)
        return

    is_user_adm = await queries.is_user_admin(session, user.telegram_id)
    is_super = user.telegram_id in settings.admin_ids

    await callback.message.edit_reply_markup(
        reply_markup=user_management_keyboard(
            user.telegram_id, 
            user.is_banned,
            is_admin=is_user_adm,
            is_super_admin=is_super
        )
    )
    await callback.answer("Ban olib tashlandi.")


# ================= 👑 ADMINLAR BOSHQARUVI =================

@router.callback_query(F.data == "admin:admins")
async def show_admins_menu(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    admins = await queries.get_all_admins(session)
    env_admins = set(settings.admin_ids)
    
    await callback.message.edit_text(
        "👑 <b>Bot adminlari ro'yxati:</b>\n\n"
        "Adminlikdan olish uchun uning ismidagi ❌ tugmasini bosing.",
        reply_markup=admins_list_keyboard(admins, env_admins),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:admins:add")
async def start_add_admin(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    await state.set_state(AdminPanel.waiting_new_admin_id) # state.py dagi waiting_new_admin_id
    await callback.message.edit_text(
        "✏️ Yangi adminning Telegram ID (raqamli) raqamini kiriting:\n"
        "Orqaga: /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminPanel.waiting_new_admin_id, F.text != "/cancel")
async def process_new_admin_id(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return
    try:
        tg_id = int(message.text.strip())
        await state.update_data(new_admin_id=tg_id)
        await state.set_state(AdminPanel.waiting_new_admin_name)
        await message.answer("✏️ Yangi admin ismini (full name) yozing:")
    except ValueError:
        await message.answer("❌ Telegram ID faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting:")


@router.message(AdminPanel.waiting_new_admin_name, F.text != "/cancel")
async def process_new_admin_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return
    data = await state.get_data()
    await queries.add_admin_user(
        session,
        telegram_id=data['new_admin_id'],
        full_name=message.text.strip()
    )
    await state.clear()
    await message.answer("✅ Yangi admin muvaffaqiyatli qo'shildi!", reply_markup=admin_panel_keyboard())


@router.callback_query(F.data.startswith("admin:admins:revoke:"))
async def delete_admin_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return
    admin_tg_id = int(callback.data.split(":")[-1])
    
    admins = await queries.get_all_admins(session)
    admin_db_id = None
    for adm in admins:
        if adm.telegram_id == admin_tg_id:
            admin_db_id = adm.id
            break
            
    if admin_db_id:
        await queries.delete_admin_user(session, admin_db_id)
        
    updated_admins = await queries.get_all_admins(session)
    env_admins = set(settings.admin_ids)
    
    await callback.message.edit_text(
        "✅ Admin tizimdan o'chirildi!\n👑 <b>Yangi ro'yxat:</b>",
        reply_markup=admins_list_keyboard(updated_admins, env_admins),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:admins:noop")
async def noop_callback(callback: CallbackQuery) -> None:
    await callback.answer("🔒 Asosiy adminni tizimdan o'chirib bo'lmaydi!", show_alert=True)


# ================= ⚙️ ESKI KANAL SOZLAMALARI =================

@router.callback_query(F.data == "admin:channel")
async def channel_settings(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, callback.from_user.id):
        await callback.answer("Ruxsat yo'q.", show_alert=True)
        return

    current = await queries.get_channel_id(session)
    await state.set_state(AdminPanel.waiting_channel_id)
    await callback.message.edit_text(
        f"⚙️ <b>Kanal sozlamalari</b>\n\n"
        f"Hozirgi kanal: <code>{current}</code>\n\n"
        f"Yangi kanal ID yoki @username yuboring.\n"
        f"Bekor qilish: /cancel",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminPanel.waiting_channel_id, F.text == "/cancel")
async def cancel_channel_change(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=admin_panel_keyboard())


@router.message(AdminPanel.waiting_channel_id, F.text)
async def set_channel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await queries.is_user_admin(session, message.from_user.id):
        return

    new_channel = message.text.strip()
    await queries.set_channel_id(session, new_channel)
    await state.clear()
    await message.answer(
        f"✅ Kanal yangilandi: <code>{new_channel}</code>",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML",
    )