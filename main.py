import os
import logging

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

from handlers import router, start_register, register_block
from states import RegisterState

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
dp = Dispatcher()

""" Регистрируем хендлер регистрации"""
dp.message.register(start_register, F.text=='Зарегистрироваться')
dp.message.register(register_block, RegisterState.regBlock)

async def main():
    """ Главная функция, запускающая обработку бота """
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")