from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from keyboards.inline.inline_buttons import start_button, main_menu_button, pament_inline_keyboard

from loader import dp, db
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from data.config import UZ_TIMEZONE


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id

    payment_status = await check_payment_status(message=message, user_id=telegram_id)
    if not payment_status:
        return

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


async def check_payment_status(message: types.Message, user_id: int) -> bool:
    """
    Foydalanuvchining to‘lov holatini tekshiradi.
    Agar foydalanuvchi obunani amalga oshirgan bo‘lsa va obuna muddati tugamagan bo‘lsa, True qaytaradi.
    Aks holda, False qaytaradi.
    """
    if message.chat.type != "private":
        return True

    user_id = message.from_user.id
    user_data = await db.select_user(telegram_id=user_id)
    if not user_data:
        return True

    now = datetime.now(ZoneInfo(UZ_TIMEZONE))
    user_register_date = user_data.get("created_at")
    if (now - user_register_date).days <= 1:
        return True

    record = await db.select_payment(user_id=user_id)

    if not record or not record.get("is_paid") or record.get("end_date") < datetime.now(timezone.utc):
        await message.answer(
            text="❌ Sizning obunangiz faol emas.\n\nIltimos, to‘lov qiling va qayta urinib ko‘ring.",
            reply_markup=pament_inline_keyboard
        )
        return False
    return True
