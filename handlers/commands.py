import os

from aiogram import Router, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from keyboards.keyboards import register_keyboard
from states import AnnounceState
from database import Database

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