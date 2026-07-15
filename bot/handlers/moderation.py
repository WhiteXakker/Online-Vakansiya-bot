import logging
from html import escape
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states.admin import AdminPanel
from config.settings import settings
from database import queries
from database.models import SubmissionStatus

router = Router(name="moderation")
logger = logging.getLogger(__name__)


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.callback_query(F.data.startswith("mod:approve:"))
async def approve_submission(
    callback: CallbackQuery,
    session: AsyncSession,
) -> None:
    # 1. Adminlik huquqini tekshirish
    if not _is_admin(callback.from_user.id):
        await callback.answer("Siz bot admini emassiz! Ruxsat yo'q.", show_alert=True)
        return

    # 2. callback_data dan ID ni to'g'ri ajratib olish
    try:
        submission_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Ariza ID sini aniqlashda xatolik.", show_alert=True)
        return

    submission = await queries.get_submission(session, submission_id)
    if not submission:
        await callback.answer("Ariza ma'lumotlar bazasidan topilmadi.", show_alert=True)
        return

    if submission.status != SubmissionStatus.PENDING:
        await callback.answer("Bu ariza allaqachon ko'rib chiqilgan!", show_alert=True)
        return

    # 3. Kanalga xabar yuborish
    try:
        channel_id = await queries.get_channel_id(session)
        channel_message = await callback.bot.send_message(
            chat_id=channel_id,
            text=submission.formatted_text,
            parse_mode="HTML"  # Formatlash buzilmasligi uchun aniq HTML yozamiz
        )
    except Exception as e:
        logger.error(f"Kanalga post yuborishda xatolik: {e}")
        await callback.answer(f"Xatolik: Kanalga yuborib bo'lmadi. Bot kanalda adminmi?", show_alert=True)
        return

    # 4. Bazada arizani yangilash
    await queries.update_submission_status(
        session,
        submission_id,
        SubmissionStatus.APPROVED,
        channel_message_id=channel_message.message_id,
    )

    # 5. Arizachiga xabar berish
    try:
        user = submission.user
        await callback.bot.send_message(
            chat_id=user.telegram_id,
            text="🎉 <b>Tabriklaymiz!</b> Arizangiz tasdiqlandi va kanalga joylandi.",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Arizachiga xabar yetkazib bo'lmadi (Foydalanuvchi botni bloklagan bo'lishi mumkin): {e}")

    # 6. Guruhdagi xabarni tahrirlash (tugmalarni tozalash)
    try:
        # Xabar matnini xavfsiz tarzda edit qilamiz
        original_text = callback.message.text or callback.message.caption or ""
        new_text = original_text + "\n\n✅ <b>QABUL QILINDI</b>"
        
        await callback.message.edit_text(
            text=new_text,
            reply_markup=None,  # Tugmalarni o'chirish!
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Guruh xabarini tahrirlashda xato: {e}")
        # Agar HTML parse xatosi bersa, oddiy matn sifatida tahrirlaymiz
        await callback.message.edit_text(
            text=original_text + "\n\n✅ QABUL QILINDI",
            reply_markup=None,
            parse_mode=None
        )

    await callback.answer("Kanalga muvaffaqiyatli joylandi!", show_alert=True)


@router.callback_query(F.data.startswith("mod:reject:"))
async def reject_submission_prompt(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer("Siz bot admini emassiz! Ruxsat yo'q.", show_alert=True)
        return

    try:
        submission_id = int(callback.data.split(":")[-1])
    except (ValueError, IndexError):
        await callback.answer("Xatolik: Ariza ID sini aniqlab bo'lmadi.", show_alert=True)
        return

    await state.set_state(AdminPanel.waiting_rejection_reason)
    await state.update_data(reject_submission_id=submission_id)
    
    # Qaysi xabarga javob yozish kerakligini bilish uchun adminga xabar yuboramiz
    await callback.message.answer(
        f"✍️ <b>Ariza #{submission_id}</b> uchun rad etish sababini yozing.\n"
        "Agar sababsiz rad etmoqchi bo'lsangiz /skip buyrug'ini yuboring.",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminPanel.waiting_rejection_reason, F.text)
async def process_rejection_reason(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if not _is_admin(message.from_user.id):
        return

    data = await state.get_data()
    submission_id = data.get("reject_submission_id")
    if not submission_id:
        await message.answer("Xatolik: Ariza ID si yo'qolgan. Qaytadan urinib ko'ring.")
        await state.clear()
        return

    reason = "" if message.text == "/skip" else message.text.strip()
    submission = await queries.get_submission(session, submission_id)
    
    if not submission:
        await message.answer("Ariza topilmadi.")
        await state.clear()
        return

    if submission.status != SubmissionStatus.PENDING:
        await message.answer("Bu ariza allaqachon ko'rib chiqilgan.")
        await state.clear()
        return

    # Statusni yangilash
    await queries.update_submission_status(
        session,
        submission_id,
        SubmissionStatus.REJECTED,
        rejection_reason=reason or None,
    )

    # Foydalanuvchini ogohlantirish
    try:
        user = submission.user
        text = "❌ <b>Arizangiz rad etildi.</b>"
        if reason:
            text += f"\n\n<b>Sabab:</b> {escape(reason)}"
        await message.bot.send_message(chat_id=user.telegram_id, text=text, parse_mode="HTML")
    except Exception as e:
        logger.warning(f"Foydalanuvchiga rad javobini yuborib bo'lmadi: {e}")

    await message.answer(f"🔴 Ariza #{submission_id} rad etildi.")
    await state.clear()