from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import F, Router

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """ Команда /start """
    user_name = message.from_user.first_name
    start_message = (f'Здравствуйте, {user_name}. Бот успешно запущен и будет информировать'
                     f' Вас о важных мероприятиях. Пожалуйста, не выклчайте звук, чтобы не пропустить их)')
    await message.answer(start_message)
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