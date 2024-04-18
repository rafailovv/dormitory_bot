import os
import logging

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from handlers.commands import router
from handlers.registration import start_register, register_block, register_car_check, register_car_data
from states import RegisterState, AnnounceState
from utils.commands import announce, announce_text, create_schedules

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
dp = Dispatcher()

""" Регистрируем хендлер регистрации """
dp.message.register(start_register, F.text=='Зарегистрироваться')
dp.message.register(register_block, RegisterState.reg_block)
dp.message.register(register_car_check, RegisterState.reg_has_car)
dp.message.register(register_car_data, RegisterState.reg_car_data)

""" Регистрируем хендлер уведомления """
dp.message.register(announce, AnnounceState.announce)

async def main():
    """ Главная функция, запускающая обработку бота """

    # Считываем данные из Excel-файла
    create_schedules("./data/Announcements.xlsx", "Sheet1", announce_text)

    # Создаем и запускаем процедуру, считывания данных из Excel-файла каждый день в 00:01
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(create_schedules, trigger="cron", hour=0, minute=1,
                      args=["./data/Announcements.xlsx", "Sheet1", announce_text])
    scheduler.start()

    # Подключаем роутеры
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")