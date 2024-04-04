import os

import json
from aiogram import Router, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from keyboards import register_keyboard, yes_or_no_keyboard
from states import RegisterState, AnnounceState
from database import Database
from utils import validate_block, validate_car_mark, validate_car_number

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
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
    commands_desc = {"start": "запуск бота",
                     "help": "показывает список команд",
                     "announce": "уведомляет всех жителей общежития"}

    help_reply = ""
    for key in commands_desc:
        help_reply += f"<b>/{key}</b> - <em>{commands_desc[key]}</em>\n"
    help_reply = help_reply.strip()

    await message.reply(help_reply, parse_mode='HTML')

@router.message(Command("announce"))
async def announce_command(message: Message, state: FSMContext):
    """ Команда /announce """
    db = Database(os.getenv('DATABASE_NAME'))
    user = db.is_user_admin(message.from_user.id)

    if user:
        await message.answer("Введите сообщение, которое вы хотите передать всем жителям общежития!")
        await state.set_state(AnnounceState.announce)
    else:
        await message.answer("У вас нет прав для использования этой команды!")

async def announce(message: Message, state: FSMContext):
    """ Вывод уведомления всем жителям общежития """
    await state.update_data(announce=message.text)
    announce_data = await state.get_data()
    announce_msg = announce_data.get("announce")

    db = Database(os.getenv('DATABASE_NAME'))
    users = db.get_all_users()

    for user in users:
        await bot.send_message(user[2], announce_msg, parse_mode="HTML")
        
    await state.clear()
    await message.reply("Это сообщение отправлено всем жителям общежития!")

async def start_register(message: Message, state: FSMContext):
    """ Регистрации """
    db = Database(os.getenv('DATABASE_NAME'))
    user = db.select_user_id(message.from_user.id)
    if(user):
        await message.answer("Вы уже зарегистрированы")
    else:
        await message.answer(f'Напишите свой блок \n'
                                f'Формат ввода: НомерБуква \n'
                                f'Например: 617А')
        await state.set_state(RegisterState.reg_block)

async def register_block(message: Message, state: FSMContext):
    """ Окончание регистрации """
    block = validate_block(message.text)
    if block:
        await state.update_data(reg_block=block)
        await state.set_state(RegisterState.reg_has_car)
        await message.answer("Отлично!\nУ вас есть машина?", reply_markup=yes_or_no_keyboard)
    else:
        await state.clear()
        await message.answer("Номер блока введен некорректно! Начните регистрацию заново.", reply_markup=register_keyboard)

async def register_car_check(message: Message, state: FSMContext):
    """ Регистрация машины при наличии """
    if message.text.strip().lower() == "да":
        # Enter car
        await state.update_data(reg_has_car=True)
        await message.answer(f"Введите марку и номер своей машины в одну строку.)\n"
                                f"Внимание, будь очень внимательны, проверь все ли ввели правильно!\n"
                                f"При вводе номера испольйте только английские символы и цифры. Будьте очень внимательны!\n"
                                f"Формат ввода: Марка Номер\n"
                                f"Например: Lamborghini A012AA\n")
        await state.set_state(RegisterState.reg_car_data)
    elif message.text.strip().lower() == "нет":
        await state.update_data(reg_has_car=False)
        reg_data = await state.get_data()
        msg = (f'Регистрация прошла успешно\n'
                f'Ваш блок: {reg_data['reg_block']}\n')
        await message.answer(msg)
        
        db = Database(os.getenv('DATABASE_NAME'))
        db.add_user(reg_data["reg_block"], int(message.from_user.id), reg_data["reg_has_car"])
        await state.clear()

async def register_car_data(message: Message, state: FSMContext):
    """ Регистрирует марку и номер машины """
    car_data = message.text.split()

    if len(car_data) > 2:
        car_data = [" ".join(car_data[:-1]), car_data[-1]]

    car_mark, car_number = car_data[0], car_data[1]

    cars_marks_base = None
    with open('./data/cars.json', 'r', encoding="utf-8") as file:
        cars_marks_base = json.load(file,)

    if validate_car_mark(car_mark, cars_marks_base) and validate_car_number(car_number):
        await state.update_data(reg_has_car=True, reg_car_data=[car_mark, car_number])
        reg_data = await state.get_data()
        msg = (f"Регистрация прошла успешно\n"
                f"Ваш блок: {reg_data['reg_block']}\n"
                f"Ваша машина: {reg_data['reg_car_data'][0]} {reg_data['reg_car_data'][1]}")
        await message.answer(msg)

        db = Database(os.getenv('DATABASE_NAME'))
        db.add_user(reg_data["reg_block"], int(message.from_user.id), reg_data["reg_has_car"], reg_data['reg_car_data'][0], reg_data['reg_car_data'][1])
        await state.clear()
    else:
        await state.clear()
        await message.answer("Данные введенны некорректно! Начните регистрацию заново.", reply_markup=register_keyboard)