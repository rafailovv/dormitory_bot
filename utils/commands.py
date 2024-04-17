import os

from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from database import Database

load_dotenv()
TOKEN_BOT = os.getenv("TOKEN_BOT")

bot = Bot(token=TOKEN_BOT, parse_mode=ParseMode.HTML)

async def announce(message: Message, state: FSMContext):
    """ Вывод уведомления всем жителям общежития """
    await state.update_data(announce=message.text)
    announce_data = await state.get_data()
    announce_msg = announce_data.get("announce")

    db = Database(os.getenv('DATABASE_NAME'))
    users = db.get_all_users()

    for user in users:
        user_id = user[1]
        await bot.send_message(user_id, announce_msg, parse_mode="HTML")
        
    await state.clear()
    await message.reply("Это сообщение отправлено всем жителям общежития!")