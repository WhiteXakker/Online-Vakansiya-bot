import os  # <-- BU JUDA MUHIM, PORTni olish uchun kerak!
import asyncio
import logging
import sys
from aiohttp import web

from bot.factory import create_bot, create_dispatcher
from database.base import init_db
from aiogram.types import BotCommand


# Buyruqlar menyusini o'rnatuvchi yordamchi funksiya
async def set_bot_commands(bot) -> None:
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
    ]
    await bot.set_my_commands(commands)


# 1. Render talab qiladigan portni tinglash uchun kichik soxta veb-sahifa
async def handle(request):
    return web.Response(text="Bot is running smoothly on Render!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render avtomatik ravishda PORT muhit o'zgaruvchisini beradi.
    port = int(os.environ.get("PORT", 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server successfully started on port {port}")

async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )

    # ==========================================
    # 🔥 MANA SHU QATORNI QO'SHDIK!
    # Web serverni asinxron fonda ishga tushiramiz:
    asyncio.create_task(start_web_server())
    # ==========================================

    # 1. Ma'lumotlar bazasini ishga tushiramiz
    await init_db()

    # 2. Bot va Dispatcher obyektlarini yaratamiz
    bot = create_bot()
    dp = create_dispatcher()

    # 3. Buyruqlar menyusini Telegramga yuklaymiz
    await set_bot_commands(bot)

    logging.info("Bot started")
    
    # 4. Botni tarmoqdan xabarlarni kutish rejimiga o'tkazamiz
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
