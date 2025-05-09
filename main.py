""" Main app """
import os
import logging

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from handlers.commands import router
from handlers.registration \
import start_register, register_block, register_car_check, register_car_data
from states import RegisterState, AnnounceState
from utils.commands \
import announce, announce_text, announce_cars, announce_car_number, \
       announce_car_message, create_schedules, \
       dormitory_payment_notification, internet_payment_notification


load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрируем хендлер регистрации
dp.message.register(start_register, F.text=='Зарегистрироваться')
dp.message.register(register_block, RegisterState.reg_block)
dp.message.register(register_car_check, RegisterState.reg_has_car)
dp.message.register(register_car_data, RegisterState.reg_car_data)

# Регистрируем хендлеры уведомления
dp.message.register(announce, AnnounceState.announce)
dp.message.register(announce_cars, AnnounceState.announce_cars)
dp.message.register(announce_car_number, AnnounceState.announce_car_number)
dp.message.register(announce_car_message, AnnounceState.announce_car_message)


async def main():
    """ Главная функция, запускающая обработку бота """

    # Считываем данные из Excel-файла
    create_schedules("./data/Announcements.xlsx", "Sheet1", announce_text)

    # Создаем планировщик задач и добавляем задачу,
    # считывания данных из Excel-файла каждый день в 00:01
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(create_schedules, trigger="cron", hour=0, minute=1,
                      args=["./data/Announcements.xlsx", "Sheet1", announce_text])

    # Добавляем задачу отправки уведомления об оплате общежития и интернета
    scheduler.add_job(dormitory_payment_notification, trigger="cron", day=9, hour=20, minute=0)
    scheduler.add_job(internet_payment_notification, trigger="cron", day=21, hour=22, minute=50)

    # Запускаем планировщик
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
