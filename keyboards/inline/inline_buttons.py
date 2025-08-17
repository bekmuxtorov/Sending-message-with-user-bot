from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_button = InlineKeyboardMarkup(row_width=2)
start_button.insert(InlineKeyboardButton(
    text="🔧 Botni sozlash", callback_data="start_button"))
start_button.insert(InlineKeyboardButton(
    text="👨‍💻 Adminga yozish", callback_data="send_message_to_admin"))

main_menu_button = InlineKeyboardMarkup(row_width=1)
main_menu_button.insert(InlineKeyboardButton(
    text="✉️ Xabar yuborish", callback_data="sending_message"))
main_menu_button.insert(InlineKeyboardButton(
    text="⏰ Xabar yuborishni rejalashtirish", callback_data="sending_message_in_another_time"))
main_menu_button.insert(InlineKeyboardButton(
    text="⚙️ Botni sozlash", callback_data="start_button"))
main_menu_button.insert(InlineKeyboardButton(
    text="📂 Mening xabarlarim", callback_data="my_messages"))
