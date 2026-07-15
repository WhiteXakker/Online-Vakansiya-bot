from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import main_menu_keyboard
from database import queries

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await queries.get_or_create_user(
        session,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Online-Vakansiya platformasiga xush kelibsiz.\n"
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard(),
    )


#  YANGI QO'SHILADIGAN /help HANDLERI
@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    help_text = (
        "❓ <b>Botdan qanday foydalaniladi?</b>\n\n"
        "Ushbu bot orqali siz Ustoz, Shogird, Sherik, Xodim yoki Ish joyi kerakligi haqida e'lonlar berishingiz mumkin.\n\n"
        "📌 <b>Asosiy buyruqlar:</b>\n"
        "• /start - Botni qayta ishga tushirish va asosiy menyuga qaytish\n"
        "• /help - Botdan foydalanish bo'yicha qo'llanma\n\n"
        "📝 <b>E'lon berish tartibi:</b>\n"
        "1️⃣ Pastdagi menyudan o'zingizga mos bo'limni tanlang (masalan: <i>Sherik kerak</i>).\n"
        "2️⃣ Bot so'ragan ma'lumotlarni ketma-ket va to'g'ri kiriting.\n"
        "3️⃣ Oxirida ma'lumotlaringiz to'g'riligini tekshirib, <b>✅ Tasdiqlash</b> tugmasini bosing.\n"
        "4️⃣ Arizangiz adminlar tomonidan ko'rib chiqilib, tasdiqlangach, kanalga joylashtiriladi.\n\n"
        "⚠️ <i>Eslatma: Arizani to'ldirishda haqiqiy va to'g'ri ma'lumotlarni kiritishingiz shart. Aks holda arizangiz rad etilishi mumkin.</i>\n\n"
        "👨‍💻<b>Dasturchi:</b> <u>@MaykiCoder</u>\n" 
        "🔹<b>Kanalimiz:</b> <i><u>@OnlineVakansiyaUz</u></i>"
    )
    await message.answer(help_text, parse_mode="HTML")