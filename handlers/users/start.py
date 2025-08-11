from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline.inline_buttons import start_button

from loader import dp


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(
        text=f"👋Assalomu alaykum {message.from_user.full_name}!\n\n📢E'loningizni avtomatik guruhlarga yuboruvchi botga xush kelibsiz!🚀\n\n📌 Bu bot yordamida sizning e’lonlaringiz siz belgilagan vaqtda va o‘zingiz belgilagan guruhlarga avtomatik yuboriladi. Endi ortiqcha vaqt sarflash shart emas — barchasi bizda avtomat!⚡\n\n👨‍💻24/7 admin nazoratida.",
        reply_markup=start_button
    )
