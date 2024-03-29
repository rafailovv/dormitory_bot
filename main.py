from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from token_bot import TOKEN_BOT
import asyncio
import logging

bot = Bot(token=TOKEN_BOT)
dp = Dispatcher()


# ru - Обработчик команды /start
# en - /start command handler
@dp.message(CommandStart())
async def start_command(message: Message):
    user_name = message.from_user.first_name
    start_message = (f'Здравствуйте, {user_name}. Бот успешно запущен и будет информировать'
                     f' Вас о важных мероприятиях. Пожалуйста, не выклчайте звук, чтобы не пропустить их)')
    await message.answer(start_message)
    await message.delete()

HELP_COMMAND = """
<b>/help</b> - <em>показывает список команд</em>
<b>/start</b> - <em>запуск бота</em>"""
# ru - Обработчик команды /help
# en - /help command handler
@dp.message(Command('help'))
async def help_command(message: Message):
    await message.reply(HELP_COMMAND, parse_mode='HTML')


async def main():
    # ru - Запуск бота
    # en - Running a bot
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

