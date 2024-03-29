import os
import logging

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: Message):
    """ Команда /start """
    user_name = message.from_user.first_name
    start_message = (f'Здравствуйте, {user_name}. Бот успешно запущен и будет информировать'
                     f' Вас о важных мероприятиях. Пожалуйста, не выклчайте звук, чтобы не пропустить их)')
    await message.answer(start_message)
    await message.delete()

@dp.message(Command('help'))
async def help_command(message: Message):
    """ Команда /help """
    commands_desc = {"start": "запуск бота",
                     "help": "показывает список команд"}

    help_reply = ""
    for key in commands_desc:
        help_reply += f"<b>/{key}</b> - <em>{commands_desc[key]}</em>\n"
    help_reply = help_reply.strip()

    await message.reply(help_reply, parse_mode='HTML')

async def main():
    """ Главная функция, запускающая обработку бота """
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")