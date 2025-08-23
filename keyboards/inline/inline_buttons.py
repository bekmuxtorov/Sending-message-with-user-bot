from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.config import TIME_BETWEEN_MESSAGE

start_button = InlineKeyboardMarkup(row_width=2)
start_button.insert(InlineKeyboardButton(
    text="🔧 Botni sozlash", callback_data="start_button"))
start_button.insert(InlineKeyboardButton(
    text="👨‍💻 Adminga yozish", callback_data="send_message_to_admin"))

main_menu_button = InlineKeyboardMarkup(row_width=1)
main_menu_button.insert(InlineKeyboardButton(
    text="✉️ Xabar yuborish", callback_data="sending_message"))
# main_menu_button.insert(InlineKeyboardButton(
#     text="⏰ Xabar yuborishni rejalashtirish", callback_data="sending_message_in_another_time"))
main_menu_button.insert(InlineKeyboardButton(
    text="⚙️ Botni sozlash", callback_data="start_button"))
# main_menu_button.insert(InlineKeyboardButton(
#     text="📂 Mening xabarlarim", callback_data="my_messages"))

done_button = InlineKeyboardMarkup(row_width=1)
done_button.insert(InlineKeyboardButton(
    text="✅ Bajardim", callback_data="done"))


def generate_time_keyboard():
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    if now.minute >= 30:
        now += timedelta(hours=1)
    else:
        now += timedelta(minutes=30)

    markup = InlineKeyboardMarkup(row_width=4)
    for i in range(48):  # 48 ta vaqt = 24 soat / 0.5 soat
        time_slot = now + timedelta(minutes=30 * i)
        label = time_slot.strftime("%H:%M %d.%m.%Y")
        markup.insert(InlineKeyboardButton(
            text=label, callback_data=f"time_{label}"))
    return markup


time_between_messages = InlineKeyboardMarkup(row_width=3)
for i in TIME_BETWEEN_MESSAGE:
    time_between_messages.insert(InlineKeyboardButton(
        text=f"{i}", callback_data=f"time_{i}"))


async def start_sending_message(sending_message_id):
    start_sending_message = InlineKeyboardMarkup(row_width=1)
    start_sending_message.insert(InlineKeyboardButton(
        text="📤 Xabar yuborishni boshlash", callback_data=f"start_sending_message:{sending_message_id}"))

    start_sending_message.insert(InlineKeyboardButton(
        text="Xabar matnini o'zgartirish", callback_data=f"update_message_text:{sending_message_id}"))
    return start_sending_message