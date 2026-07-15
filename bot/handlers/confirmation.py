from html import escape
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import moderation_keyboard
from bot.keyboards.reply import main_menu_keyboard
from config.settings import settings
from database import queries
from database.models import SubmissionStatus

router = Router(name="confirmation")


async def _get_moderation_chat_id(session: AsyncSession) -> int | str:
    if settings.moderation_chat_id:
        return settings.moderation_chat_id
    return settings.admin_ids[0]


@router.callback_query(F.data == "confirm:cancel")
async def cancel_submission(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "❌ Arizangiz bekor qilindi.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm:submit")
async def submit_for_moderation(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    data = await state.get_data()
    category = data.get("category")
    form_data = data.get("form_data")
    formatted_text = data.get("formatted_text")

    if not category or not form_data or not formatted_text:
        await callback.answer("Ma'lumotlar topilmadi. Qaytadan boshlang.", show_alert=True)
        await state.clear()
        return

    user = await queries.get_or_create_user(
        session,
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=callback.from_user.full_name,
    )

    submission = await queries.create_submission(
        session,
        user_id=user.id,
        category=category,
        form_data=form_data,
        formatted_text=formatted_text,
    )

    moderation_chat = await _get_moderation_chat_id(session)
    
    # 1. Matndagi HTML xatolaridan qochish uchun ma'lumotlarni escape qilamiz
    safe_fullname = escape(callback.from_user.full_name or "Mijoz")
    safe_username = escape(callback.from_user.username or "yoq")
    
    # 2. Moderatsiya xabarining matnini tayyorlaymiz
    moderation_text = (
        f"🆕 <b>Yangi ariza #{submission.id}</b>\n"
        f"👤 <b>Foydalanuvchi:</b> {safe_fullname} "
        f"(@{safe_username}) — <b>ID:</b> <code>{callback.from_user.id}</code>\n\n"
        f"{formatted_text}"
    )

    try:
        # 3. Guruhga xabarni tugmalari (reply_markup) bilan birga yuboramiz
        mod_message = await callback.bot.send_message(
            chat_id=moderation_chat,
            text=moderation_text,
            parse_mode="HTML",
            reply_markup=moderation_keyboard(submission.id),  # Tugmani aniq ulaymiz!
            disable_web_page_preview=True
        )
    except Exception as e:
        # Agar formatted_text ichida qandaydir HTML xatosi bo'lsa, plain text yuboramiz
        print(f"Xabar yuborishda xatolik yuz berdi: {e}")
        clean_text = (
            f"🆕 Yangi ariza #{submission.id}\n"
            f"👤 Foydalanuvchi: {callback.from_user.full_name} "
            f"(@{callback.from_user.username or 'yoq'}) — ID: {callback.from_user.id}\n\n"
            f"{formatted_text.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')}"
        )
        mod_message = await callback.bot.send_message(
            chat_id=moderation_chat,
            text=clean_text,
            parse_mode=None,
            reply_markup=moderation_keyboard(submission.id),  # Har qanday holatda ham tugma ulanadi!
            disable_web_page_preview=True
        )

    await queries.update_submission_status(
        session,
        submission.id,
        SubmissionStatus.PENDING,
        moderation_message_id=mod_message.message_id,
    )

    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        "✅ Arizangiz adminlarga yuborildi. Tasdiqlangandan so'ng kanalga joylanadi.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()