import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot, db

from data.config import SAVE_GROUP_ID, CARD_NUMBER, CARDHOLDER, PAYMENT_AMOUNT, PAYMENT_MESSAGE_TOPIC_ID
from keyboards.inline.inline_buttons import send_payment_check, main_menu_button, built_invoice_in_group, pament_inline_keyboard
from states.state_payment import CheckPayment

from data.config import UZ_TIMEZONE


@dp.callback_query_handler(text="payment")
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer(
        text=f"💵Botdan foydalanish uchun obuna bo‘lishingiz kerak.\n\n💳<code>{CARD_NUMBER}</code>\n{CARDHOLDER}\nSumma: {PAYMENT_AMOUNT} UZS\n\nTo‘lovni amalga oshirgach, tasdiqlash uchun quyidagi tugma bilan chekni yuboring.",
        reply_markup=send_payment_check
    )


@dp.callback_query_handler(text="send_payment_check")
async def bot_echo(call: types.CallbackQuery, state: FSMContext):

    await call.message.answer(
        text="📤 To‘lov chekini rasmini quyiga yuboring."
    )
    await call.message.delete()
    await CheckPayment.send_invoice.set()


@dp.message_handler(state=CheckPayment.send_invoice, content_types=[types.ContentType.DOCUMENT, types.ContentType.PHOTO])
async def bot_echo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await message.delete()
    await message.answer(
        text="✅ Yaxshi, to‘lov muaffaqiyatli amalga oshirildi.\n\nBotdan foydalanishni davom ettirishingiz mumkin.",
        reply_markup=main_menu_button
    )
    payment_data = await db.add_payment(user_id=user_id)
    payment_id = payment_data.get("id")
    username_or_id = f"""@{message.from_user.username}""" if message.from_user.username else message.from_user.id
    if message.photo:
        photo = message.photo[-1].file_id  # eng sifatli variantni olish
        msg = await bot.send_photo(
            chat_id=SAVE_GROUP_ID,
            message_thread_id=PAYMENT_MESSAGE_TOPIC_ID,
            photo=photo,
            caption=f"💳 Yangi to‘lov hujjati\n\n👤 User: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}\n🪪Username: {username_or_id}",
            reply_markup=await built_invoice_in_group(payment_id, None)
        )

    elif message.document:
        doc = message.document.file_id
        msg = await bot.send_document(
            chat_id=SAVE_GROUP_ID,
            message_thread_id=PAYMENT_MESSAGE_TOPIC_ID,
            document=doc,
            caption=f"💳 Yangi to‘lov hujjati\n\n👤 User: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}",
            reply_markup=await built_invoice_in_group(payment_id, None)
        )

    message_id = msg.message_id
    await bot.edit_message_reply_markup(
        chat_id=SAVE_GROUP_ID,
        message_id=message_id,
        reply_markup=await built_invoice_in_group(payment_id, message_id)
    )
    await state.finish()


@dp.message_handler(state=CheckPayment.send_invoice)
async def bot_echo(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text="To'lov chekini faqat rasm yoki fayl ko'rinishida yuborishingiz mumkin. Iltimos, qayta urinib ko‘ring.",
    )
    await CheckPayment.send_invoice.set()


@dp.callback_query_handler(lambda c: c.data.startswith("accept_payment:"))
async def process_accept_payment(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.split(":")
    payment_id = data[1]
    message_id = data[2]
    payment_data = await db.select_payment(id=int(payment_id))
    user_data = await db.select_user(telegram_id=payment_data.get("user_id"))
    accepted_username_or_first_name = f"@{callback_query.from_user.username}" if callback_query.from_user.username else callback_query.from_user.first_name
    start_date = datetime.now(ZoneInfo(UZ_TIMEZONE))
    end_date = datetime.now(ZoneInfo(UZ_TIMEZONE)) + timedelta(days=30)
    await db.update_payment(
        payment_id=int(payment_id),
        start_date=datetime.now(ZoneInfo(UZ_TIMEZONE)),
        end_date=datetime.now(ZoneInfo(UZ_TIMEZONE)) + timedelta(days=30),
        is_paid=True,
        accepted_username_or_first_name=accepted_username_or_first_name,
        is_new_payment=False
    )

    username_or_id = f"""@{user_data.get("username")}""" if user_data.get(
        "username") else user_data.get("telegram_id")
    await bot.edit_message_caption(
        chat_id=SAVE_GROUP_ID,
        message_id=message_id,
        caption=f"""✅ To‘lov tasdiqlandi!\n\n👤 User: {user_data.get("first_name")}\n🆔 ID: {user_data.get('telegram_id')}\n🪪Username: {username_or_id}\n⚡️Tasdiqlagan shaxs: {accepted_username_or_first_name}\n📅Davr: {start_date.strftime("%Y-%m-%d %H:%M")} - {end_date.strftime("%Y-%m-%d %H:%M")}""",
        reply_markup=None
    )


@dp.callback_query_handler(lambda c: c.data.startswith("cancel_payment:"))
async def process_accept_payment(callback_query: types.CallbackQuery):
    data = callback_query.data.split(":")
    payment_id = data[1]
    message_id = int(data[2])
    msg = await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"#{payment_id} #{message_id}\n\n❓ Bekor qilinish sababini reply orqali yozing.",
        reply_to_message_id=callback_query.message.message_id
    )
    await bot.edit_message_text(
        text=f"#{payment_id} #{message_id} #{msg.message_id}\n\n❓ Bekor qilinish sababini reply orqali yozing.",
        chat_id=callback_query.message.chat.id,
        message_id=msg.message_id
    )


@dp.message_handler()
async def cancel_payment_reason(message: types.Message):
    if not message.reply_to_message:
        return

    orig_msg = message.reply_to_message

    try:
        matches = re.findall(r"#(\d+)", orig_msg.text)
        if len(matches) >= 2:
            payment_id = int(matches[0])
            message_id = int(matches[1])
            delete_message_id = int(matches[2])
        else:
            return
    except Exception as e:
        print(e)
        return

    reason = message.text.strip()
    accepted_username_or_first_name = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    await db.update_payment(
        payment_id=payment_id,
        is_paid=False,
        accepted_username_or_first_name=accepted_username_or_first_name,
        is_new_payment=False,
        reason_for_cancellation=reason
    )

    payment_data = await db.select_payment(id=int(payment_id))
    user_data = await db.select_user(telegram_id=payment_data.get("user_id"))
    username_or_id = f"""@{user_data.get("username")}""" if user_data.get(
        "username") else user_data.get("telegram_id")
    await bot.edit_message_caption(
        chat_id=SAVE_GROUP_ID,
        message_id=message_id,
        caption=f"""💥To‘lov bekor qilindi!\n\n👤 User: {user_data.get("first_name")}\n🆔 ID: {user_data.get('telegram_id')}\n🪪 Username: {username_or_id}\n⚡️ Tasdiqlagan shaxs: {accepted_username_or_first_name}\n\n📅Sabab: {reason}""",
        reply_markup=None
    )
    await bot.send_message(
        chat_id=user_data.get("telegram_id"),
        text=f"❌ Sizning to‘lovingiz bekor qilindi!\n\nSabab: \n<i>{reason}</i>\n\nTo‘lovni qayta amalga oshirishingiz mumkin.",
        reply_markup=pament_inline_keyboard
    )
    try:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=delete_message_id
        )
        await message.delete()
    except Exception as e:
        print(e)
        pass
    # if not reason:
    #     await message.answer("❌ Iltimos, bekor qilish sababini yozing.")
    #     return

    # payment_data = await db.select_payment(id=int(payment_id))
    # user_data = await db.select_user(telegram_id=payment_data.get("user_id"))
    # accepted_username_or_first_name = f"@{callback_query.from_user.username}" if callback_query.from_user.username else callback_query.from_user.first_name
    # start_date = datetime.now(ZoneInfo(UZ_TIMEZONE))
    # end_date = datetime.now(ZoneInfo(UZ_TIMEZONE)) + timedelta(days=30)
    # await db.update_payment(
    #     payment_id=int(payment_id),
    #     start_date=datetime.now(ZoneInfo(UZ_TIMEZONE)),
    #     end_date=datetime.now(ZoneInfo(UZ_TIMEZONE)) + timedelta(days=30),
    #     is_paid=True,
    #     accepted_username_or_first_name=accepted_username_or_first_name,
    #     is_new_payment=False
    # )

    # username_or_id = f"""@{user_data.get("username")}""" if user_data.get(
    #     "username") else user_data.get("telegram_id")
    # await bot.edit_message_caption(
    #     chat_id=SAVE_GROUP_ID,
    #     message_id=message_id,
    #     caption=f"""✅ To‘lov tasdiqlandi!\n\n👤 User: {user_data.get("first_name")}\n🆔 ID: {user_data.get('telegram_id')}\n🪪Username: {username_or_id}\n⚡️Tasdiqlagan shaxs: {accepted_username_or_first_name}\n📅Davr: {start_date.strftime("%Y-%m-%d %H:%M")} - {end_date.strftime("%Y-%m-%d %H:%M")}""",
    #     reply_markup=None
    # )
    # await state.update_data(time_between_messages=int(time_value))

    # all_data = await state.get_data()
    # sending_message_id = await db.add_message(
    #     user_id=callback_query.from_user.id,
    #     message_text=all_data['message_text'],
    #     message_id=str(all_data['message_id']),
    #     sending_interval=all_data['time_between_messages']
    # )
    # await callback_query.message.answer(
    #     text=f"Xabarlar yuborilish oralig'i {time_value} minutga o'rnatildi.",
    #     reply_markup=await start_sending_message(sending_message_id)
    # )
    # await callback_query.message.delete()
    # await state.finish()
