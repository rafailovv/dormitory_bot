import os

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import pandas as pd

from database import Database
from states import AnnounceState
from utils.validation import validate_car_number


load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def announce(message: Message, state: FSMContext):
    """ Вывод уведомления всем жителям общежития """
    
    if message.text == "/cancel":
        await state.clear()
        await message.reply("Ничего не произошло")
        return
    
    await state.update_data(announce=message.text)
    announce_data = await state.get_data()
    announce_msg = announce_data.get("announce")

    db = Database(os.getenv("DATABASE_NAME"))
    users = db.get_all_users()
    
    for user in users:
        user_id = user[1] # telegram_id selection
        await bot.send_message(user_id, announce_msg, parse_mode="HTML")
        
    await state.clear()
    await message.reply("Это сообщение отправлено всем жителям общежития!")


async def announce_cars(message: Message, state: FSMContext):
    """ Вывод уведомления всем жителям общежития, у которых есть машина """
    
    if message.text == "/cancel":
        await state.clear()
        await message.reply("Ничего не произошло")
        return
    
    await state.update_data(announce_cars=message.text)
    announce_cars_data = await state.get_data()
    announce_cars_msg = announce_cars_data.get("announce_cars")

    db = Database(os.getenv("DATABASE_NAME"))
    users = db.get_all_users_with_car()
    
    for user in users:
        user_id = user[1] # telegram_id selection
        await bot.send_message(user_id, announce_cars_msg, parse_mode="HTML")
        
    await state.clear()
    await message.reply("Это сообщение отправлено всем жителям общежития, у которых есть машина!")


async def announce_car_number(message: Message, state: FSMContext):
    """ Ввод номера машины, владельцу которой будет отправленно сообщение """
    
    if message.text == "/cancel":
        await state.clear()
        await message.reply("Ничего не произошло")
        return
    
    await state.update_data(announce_car_number=message.text.strip().upper())
    announce_car = await state.get_data()
    car_number = announce_car.get("announce_car_number")
    
    if validate_car_number(car_number):
        db = Database(os.getenv("DATABASE_NAME"))
        user = db.get_user_by_car_number(car_number)
        
        if user:
            await message.reply("Введите сообщение, которое вы хотите отправить владельцу машины!")
            await state.set_state(AnnounceState.announce_car_message)
        else:
            await message.reply("Пользователь с такими номерами машины не найден!")
            await state.clear()
    else:
        await state.clear()
        await message.reply("Номера машины введены некорректно!\nФормат ввода: A123BC")


async def announce_car_message(message: Message, state: FSMContext):
    """ Ввод сообщения, которое будет отправленно владельцу машины """
    
    if message.text == "/cancel":
        await state.clear()
        await message.reply("Ничего не произошло")
        return
    
    await state.update_data(announce_car_message=message.text.strip())
    announce_car = await state.get_data()
    car_number = announce_car.get("announce_car_number")
    car_message = announce_car.get("announce_car_message")
    
    db = Database(os.getenv("DATABASE_NAME"))
    user = db.get_user_by_car_number(car_number)
    
    if user:
        user_id = user[1]
        await bot.send_message(user_id, car_message, parse_mode="HTML")
        await message.reply(f"Это сообщение отправленно владельцу машины с номерами: {car_number}")
        await state.clear()


async def announce_text(msg):
    """ Вывод сообщения всем жителям общежития """
    
    db = Database(os.getenv("DATABASE_NAME"))
    users = db.get_all_users()

    for user in users:
        user_id = user[1] # telegram_id selection
        await bot.send_message(user_id, msg, parse_mode="HTML")


async def dormitory_payment_notification():
    """ Вывод сообщения всем жителям общежития об оплате общежития """
    
    db = Database(os.getenv("DATABASE_NAME"))
    users = db.get_all_users()
    
    profile_authorization_link = os.getenv("PROFILE_AUTHORIZATION_LINK")
    msg = ("<b><i>Дорогие жители общежития!</i></b>\n"
           f"Не забудьте <a href='{profile_authorization_link}'>оплатить</a> общежитие, сегодня крайний срок оплаты!")
    
    for user in users:
        user_id = user[1] # telegram_id selection
        await bot.send_message(user_id, msg, parse_mode="HTML")


async def internet_payment_notification():
    """ Вывод сообщения всем жителям общежития об оплате интернета """
    
    db = Database(os.getenv("DATABASE_NAME"))
    users = db.get_all_users()
    
    internet_payment_link = os.getenv("INTERNET_PAYMENT_LINK") if os.getenv("INTERNET_PAYMENT_LINK") is not None else "#"
    msg = ("<b><i>Дорогие жители общежития!</i></b>\n"
           f"Не забудьте <a href='{internet_payment_link}'>оплатить</a> интернет, близится конец месяца!")
    
    for user in users:
        user_id = user[1]
        await bot.send_message(user_id, msg, parse_mode="HTML")
        

def create_schedules(filename="./data/Announcements.xlsx", sheet_name="Sheet1", myfunc=None):
    """ Функция, создающая процедуры для вывода уведомлений из Excel-файла """
    
    df = pd.read_excel(filename, sheet_name=sheet_name)
    df["Дата начала"] = pd.to_datetime(df["Дата начала"]).dt.strftime("%d.%m.%Y")
    df["Дата окончания"] = pd.to_datetime(df["Дата окончания"]).dt.strftime("%d.%m.%Y")
    df["Дата уведомления"] = pd.to_datetime(df["Дата уведомления"])
    df["Дополнительная информация"] = df["Дополнительная информация"].fillna('')

    # Создаем обработчик, добавляем задания, запускаем обработчик
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    for i in range(len(df)):
        msg = (f'<b>{df["Название задания"][i]}</b>\n'
        f'Дата начала: <i>{df["Дата начала"][i]}</i>\n'
        f'Дата окончания: <i>{df["Дата окончания"][i]}</i>\n')
        if df["Дополнительная информация"][i]:
            msg += f'{df["Дополнительная информация"][i]}\n'
        
        time = str(df["Время уведомления"][i])
        hour = int(time[:time.index(':')])
        minute_with_seconds = time[time.index(':')+1:]
        minute = int(minute_with_seconds[:minute_with_seconds.index(':')])

        scheduler.add_job(myfunc, trigger="cron",
                        hour=hour, minute=minute,
                        start_date=df["Дата уведомления"][i],
                        end_date=(df["Дата уведомления"][i] + pd.DateOffset(days=1)),
                        kwargs={"msg": msg})
    scheduler.start()