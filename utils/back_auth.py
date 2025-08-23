from keyboards.inline.inline_buttons import start_button


async def back_auth(telegram_id):
    from loader import bot
    await bot.send_message(
        chat_id=telegram_id,
        text=f"⚙️ Botdan foydalanish uchun dastlab sozlashni amalga oshiring.",
        reply_markup=start_button
    )
