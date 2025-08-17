from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline.inline_buttons import start_button, main_menu_button

from loader import dp, db


# @dp.message_handler(CommandStart())
# async def bot_start(message: types.Message):
#     await message.answer(
#         text=f"👋Assalomu alaykum {message.from_user.full_name}!\n\n📢E'loningizni avtomatik guruhlarga yuboruvchi botga xush kelibsiz!🚀\n\n📌 Bu bot yordamida sizning e’lonlaringiz siz belgilagan vaqtda va o‘zingiz belgilagan guruhlarga avtomatik yuboriladi. Endi ortiqcha vaqt sarflash shart emas — barchasi bizda avtomat!⚡\n\n👨‍💻24/7 admin nazoratida.",
#         reply_markup=start_button
#     )

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    username = message.from_user.username

    user = await db.select_user(telegram_id=telegram_id)
    session = await db.select_only_session_data(user_id=telegram_id)

    if user and session:
        await message.answer(
            text=f"👋Assalomu alaykum {message.from_user.full_name}!\n\n"
            f"✅ Sizning akkauntingiz allaqachon sozlangan. Botdan foydalanishni davom etishingiz mumkin 🚀",
            reply_markup=main_menu_button
        )
    else:
        if not user:
            await db.add_user(
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                username=username
            )
        await message.answer(
            text=f"👋Assalomu alaykum {message.from_user.full_name}!\n\n"
            f"⚙️ Botdan foydalanish uchun dastlab sozlashni amalga oshiring.",
            reply_markup=start_button
        )
