from aiogram import types

from loader import dp


# Echo bot
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    if message.chat.type != "private":
        return
    await message.answer(message.text)
