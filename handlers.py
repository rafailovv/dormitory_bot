import os

from aiogram import F, Router, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from keyboards import register_keyboard
from states import RegisterState, AnnounceState
from database import Database
from utils import validate_block

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)
router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """ Команда /start """
    user_name = message.from_user.first_name
    start_message = (f'Здравствуйте, {user_name}. Бот успешно запущен и будет информировать'
                        f' Вас о важных мероприятиях. Пожалуйста, не выключайте звук, чтобы не пропустить их)')
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
                                f'Формат блока: НомерБуква \n'
                                f'Например: 617А')
        await state.set_state(RegisterState.reg_block)

async def register_block(message: Message, state: FSMContext):
    """ Окончание регистрации """
    block = validate_block(message.text)
    if block:
        await state.update_data(reg_block=block)
        reg_data = await state.get_data()
        reg_block = reg_data.get('reg_block')
        msg = (f'Регистрация прошла успешно \n'
            f'Ваш блок: {reg_block}')
        await message.answer(msg)
        db = Database(os.getenv('DATABASE_NAME'))
        db.add_user(reg_block, message.from_user.id)
        await state.clear()
    else:
        await state.clear()
        await message.answer("Номер блока введен некорректно! Начните регистрацию заново.", reply_markup=register_keyboard)