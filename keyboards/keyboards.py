""" Keyboards """
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

register_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Зарегистрироваться")
    ]
], resize_keyboard=True,  one_time_keyboard=True)

yes_or_no_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Да"),
        KeyboardButton(text="Нет")
    ]
], resize_keyboard=True, one_time_keyboard=True)
