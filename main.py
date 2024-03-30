import os
import logging

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

from handlers import router

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

async def main():
    """ Главная функция, запускающая обработку бота """
    bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")