from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_button = InlineKeyboardMarkup(row_width=2)
start_button.insert(InlineKeyboardButton(
    text="🔧 Botni sozlash", callback_data="start_button"))
start_button.insert(InlineKeyboardButton(
    text="👨‍💻 Adminga yozish", callback_data="send_message_to_admin"))
