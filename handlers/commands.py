import os

from aiogram import Router, Bot
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import pandas as pd

from keyboards.keyboards import register_keyboard
from states import AnnounceState
from database import Database
from utils.commands import create_schedules, announce_text


load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    """ Команда /start """
    user_name = message.from_user.first_name
    start_message = (f'Здравствуйте, {user_name}. Бот успешно запущен и будет информировать'
                        f'Вас о важных мероприятиях. Пожалуйста, не выключайте звук, чтобы не пропустить их)')
    await message.answer(start_message, reply_markup=register_keyboard)
    await message.delete()


@router.message(Command("help"))
async def help_command(message: Message):
    """ Команда /help """
    commands_desc = {"start": "Запуск бота",
                     "help": "Показывает список команд",
                     "info": "Показывает информацию для жителей общежития (Номер общежития и т.п.)",
                     "announce": "Уведомляет всех жителей общежития (Только для админов)",
                     "check_schedules": "Проверяет файл с объявлениями и обновляет их (Только для админов)",
                     "announce_cars": "Уведомляет всех владельцев автомобилей, проживающих в общежитии (Только для админов)",
                     "announce_car": "Уведомяет жильца общежития с определенным номером машины (Только для админов)",
                     "cancel": "Отмена выполнение некоторых команд"}

    help_reply = ""
    for key in commands_desc:
        help_reply += f"<b>/{key}</b> - <em>{commands_desc[key]}</em>\n"
    help_reply = help_reply.strip()

    await message.reply(help_reply, parse_mode='HTML')
    
    
@router.message(Command("info"))
async def help_command(message: Message):
    """ Команда /info """
    
    reply_message = ("Номер общежития: <a href='tel:+79779437901'>+7 (977) 943-79-01</a>\n"
                    "Почта для отправки чеков об оплате общежития: <a href='mailto:obsh4miit@yandex.ru'>obsh4miit@yandex.ru</a>\n"
                    "Время смены постельного белья: \n"
                    "Пн-Ср 9:00-12:00, 16:00-18:00\n")
    
    await message.reply(reply_message, parse_mode="HTML")


@router.message(Command("announce"))
async def announce_command(message: Message, state: FSMContext):
    """ Команда /announce """
    db = Database(os.getenv("DATABASE_NAME"))
    user = db.is_user_admin(message.from_user.id)

    if user:
        await message.answer("Введите сообщение, которое вы хотите передать всем жителям общежития!")
        await state.set_state(AnnounceState.announce)
    else:
        await message.answer("У вас нет прав для использования этой команды!")


@router.message(Command("announce_cars"))
async def announce_cars(message: Message, state: FSMContext):
    """ Команда /announce_cars """
    
    db = Database(os.getenv("DATABASE_NAME"))
    user = db.is_user_admin(message.from_user.id)
    
    if user:
        await message.answer("Введите сообщение, которое вы хотите передать всем жителям общежития, у которых есть машина!")
        await state.set_state(AnnounceState.announce_cars)
    else:
        await message.answer("У вас нет прав для использования этой команды!")


@router.message(Command("announce_car"))
async def announce_car(message: Message, state: FSMContext):
    """ Команда /announce_car """
    
    db = Database(os.getenv("DATABASE_NAME"))
    user = db.is_user_admin(message.from_user.id)
    
    if user:
        await message.answer("Введите номер машины, владельцу которой вы хотите передать сообщение!")
        await state.set_state(AnnounceState.announce_car_number)
    else:
        await message.answer("У вас нет прав для использования этой команды!")


@router.message(Command("check_schedules"))
async def check_schedule(message: Message, state: FSMContext):
    """ Команда /check_schedule """
    
    db = Database(os.getenv("DATABASE_NAME"))
    user = db.is_user_admin(message.from_user.id)
    
    if user:
        try:
            # Считываем данные из Excel-файла
            create_schedules("./data/Announcements.xlsx", "Sheet1", announce_text)

            # Создаем планировщик задач и добавляем задачу, считывания данных из Excel-файла каждый день в 00:01
            scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
            scheduler.add_job(create_schedules, trigger="cron", hour=0, minute=1,
                            args=["./data/Announcements.xlsx", "Sheet1", announce_text])
            
            scheduler.start()
            
            await message.answer("Данные обновились!")
        except:
            await message.answer("Неопознанная ошибка")
    else:
        await message.answer("У вас нет прав для использования этой команды!")