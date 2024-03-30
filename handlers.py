import os

from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import F, Router

from keyboards import register_keyboard
from states import RegisterState
from database import Database

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """ Команда /start """
    user_name = message.from_user.first_name
    start_message = (f'Здравствуйте, {user_name}. Бот успешно запущен и будет информировать'
                        f' Вас о важных мероприятиях. Пожалуйста, не выключайте звук, чтобы не пропустить их)')
    await message.answer(start_message, reply_markup=register_keyboard)
    await message.delete()

@router.message(Command('help'))
async def help_command(message: Message):
    """ Команда /help """
    commands_desc = {"start": "запуск бота",
                     "help": "показывает список команд"}

    help_reply = ""
    for key in commands_desc:
        help_reply += f"<b>/{key}</b> - <em>{commands_desc[key]}</em>\n"
    help_reply = help_reply.strip()

    await message.reply(help_reply, parse_mode='HTML')


async def start_register(message: Message, state: FSMContext):
    db = Database(os.getenv('DATABASE_NAME'))
    users = db.select_user_id(message.from_user.id)
    if(users):
        await message.answer("Вы уже зарегистрированы")
    else:
        await message.answer(f'Напишите свой блок \n'
                                f'Формат блока: НомерБуква \n'
                                f'Например: 617А')
        await state.set_state(RegisterState.regBlock)


async def register_block(message: Message, state: FSMContext):
    await state.update_data(regblock=message.text)
    reg_data = await state.get_data()
    reg_block = reg_data.get('regblock')
    msg = (f'Регистрация прошла успешно \n'
           f'Ваш блок: {reg_block}')
    await message.answer(msg)
    db = Database(os.getenv('DATABASE_NAME'))
    db.add_user(reg_block, message.from_user.id)
    await state.clear()