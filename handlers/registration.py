""" Registration module """
import os

import json
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from keyboards.keyboards import register_keyboard, yes_or_no_keyboard
from states import RegisterState
from database import Database
from utils.validation import validate_block, validate_car_mark, validate_car_number


load_dotenv()


async def start_register(message: Message, state: FSMContext):
    """ Регистрации """
    db = Database(os.getenv('DATABASE_NAME'))
    user = db.select_user_id(message.from_user.id)

    if user:
        await message.answer("Вы уже зарегистрированы")
    else:
        await message.answer("Напишите свой блок \n"
                             "Формат ввода: НомерБуква \n"
                             "Например: 617А")
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
        await message.answer("Номер блока введен некорректно! Начните регистрацию заново.",
                             reply_markup=register_keyboard)

async def register_car_check(message: Message, state: FSMContext):
    """ Регистрация машины при наличии """
    if message.text.strip().lower() == "да":
        await state.update_data(reg_has_car=True)
        await message.answer("Введите марку и номер своей машины в одну строку.\n"
                             "Внимание, будь очень внимательны, проверь все ли ввели правильно!\n"
                             "При вводе номера испольйте только английские символы и цифры. "
                             "Будьте очень внимательны!\n"
                             "Формат ввода: Марка Номер\n"
                             "Например: Lamborghini A012AA\n")
        await state.set_state(RegisterState.reg_car_data)
    elif message.text.strip().lower() == "нет":
        await state.update_data(reg_has_car=False)
        reg_data = await state.get_data()
        msg = (f"Регистрация прошла успешно\n"
                f"Ваш блок: {reg_data['reg_block']}\n")
        await message.answer(msg)

        db = Database(os.getenv('DATABASE_NAME'))
        db.add_user(reg_data["reg_block"], int(message.from_user.id), reg_data["reg_has_car"])
        await state.clear()

async def register_car_data(message: Message, state: FSMContext):
    """ Регистрирует марку и номер машины """
    car_data = message.text.strip()

    if car_data.count(" ") != 1:
        await state.clear()
        await message.answer("Данные введенны некорректно! Начните регистрацию заново.",
                             reply_markup=register_keyboard)
        return

    car_mark, car_number = car_data.split()
    car_mark = car_mark.title()
    car_number = car_number.upper()
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
        db.add_user(reg_data["reg_block"],
                    int(message.from_user.id),
                    reg_data["reg_has_car"],
                    reg_data['reg_car_data'][0],
                    reg_data['reg_car_data'][1])
        await state.clear()
    else:
        await state.clear()
        await message.answer("Данные введенны некорректно! Начните регистрацию заново.",
                             reply_markup=register_keyboard)
