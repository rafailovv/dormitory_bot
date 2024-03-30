import os
import logging

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

from handlers import router, start_register, register_block, announce
from states import RegisterState, AnnounceState

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
dp = Dispatcher()

""" Регистрируем хендлер регистрации """
dp.message.register(start_register, F.text=='Зарегистрироваться')
dp.message.register(register_block, RegisterState.reg_block)

""" Регистрируем хендлер уведомления """
dp.message.register(announce, AnnounceState.announce)

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