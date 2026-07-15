import asyncio
import logging
import sys

from bot.factory import create_bot, create_dispatcher
from database.base import init_db
from aiogram.types import BotCommand


# Buyruqlar menyusini o'rnatuvchi yordamchi funksiya (main tashqarisida yozish chiroyliroq)
async def set_bot_commands(bot) -> None:
    commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
    )

    # 1. Ma'lumotlar bazasini ishga tushiramiz
    await init_db()

    # 2. Bot va Dispatcher obyektlarini yaratamiz
    bot = create_bot()
    dp = create_dispatcher()

    # 3. ENG MUHIM QISM: Buyruqlar menyusini Telegramga yuklaymiz!
    await set_bot_commands(bot)

    logging.info("Bot started")
    
    # 4. Botni tarmoqdan xabarlarni kutish rejimiga o'tkazamiz
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())