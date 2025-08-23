from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db, bot
from keyboards.inline.inline_buttons import done_button, main_menu_button, time_between_messages, start_sending_message
from utils.using_folders import get_ids_by_filter_name, send_to_all_groups, send_to_all_groups_with_scheduled
from states.sending_message import SendingMessageState
from keyboards.default.default_buttons import back_button

from data.config import SAVE_GROUP_ID, SAVE_MESSAGE_TOPIC_ID


@dp.callback_query_handler(text="sending_message")
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        text="Xabar yuborish uchun yubormoqchi bo'lgan guruhlaringizni barchasini bir guruhga ya'ni Avto papkasiga yig'ing. Bu bo'yicha yuqorida video ko'rsatma yuborildi.",
        reply_markup=done_button
    )


@dp.callback_query_handler(text="done")
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    ids = await get_ids_by_filter_name(call.from_user.id)
    await call.message.delete()
    if not ids:
        await call.message.answer(
            text="Avto papkasida hech qanday guruh topilmadi. Iltimos, Avto papkasini video bo'yicha yarating va unga guruh qo'shing.",
            reply_markup=done_button
        )
        return

    await call.message.answer(
        text="Guruhlarga yubormoqchi bo'lgan xabaringizni matnini yuboring yoki xabarni shu yerga forward qiling.",
        reply_markup=back_button
    )
    await SendingMessageState.message_text.set()


@dp.message_handler(state=SendingMessageState.message_text)
async def send_message_to_groups(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    text = message.text.strip()

    if not text:
        await message.answer(
            text="Iltimos, guruhlarga yubormoqchi bo'lgan xabaringizni matnini yuboring yoki xabarni shu yerga forward qiling.",
            reply_markup=back_button
        )
        return

    try:
        forwarded_msg = await bot.forward_message(
            chat_id=SAVE_GROUP_ID,            # saqlash guruhi ID
            from_chat_id=telegram_id,
            message_id=message.message_id,
            message_thread_id=SAVE_MESSAGE_TOPIC_ID  # faqat forumli supergroup bo‘lsa
        )
    except Exception as e:
        await message.answer(f"❌ Xabarni saqlashda xatolik: {e}")
        return

    # 🔹 Forward qilingan message_id ni FSM state’ga yozamiz
    await state.update_data(
        message_text=text,
        message_id=forwarded_msg.message_id
    )

    # 🔹 Keyingi step – vaqt intervalini so‘raymiz
    await message.answer(
        text="⚡️Xabarlar yuborilish oralig'ini quyidan tanglang (minutda):",
        reply_markup=time_between_messages
    )
    await SendingMessageState.time_between_messages.set()


# #

@dp.callback_query_handler(lambda c: c.data.startswith("time_"), state=SendingMessageState.time_between_messages)
async def process_time_selection(callback_query: types.CallbackQuery, state: FSMContext):
    time_value = callback_query.data.split("_")[1]
    await state.update_data(time_between_messages=int(time_value))

    all_data = await state.get_data()
    sending_message_id = await db.add_message(
        user_id=callback_query.from_user.id,
        message_text=all_data['message_text'],
        message_id=str(all_data['message_id']),
        sending_interval=all_data['time_between_messages']
    )
    await callback_query.message.answer(
        text=f"Xabarlar yuborilish oralig'i {time_value} minutga o'rnatildi.",
        reply_markup=await start_sending_message(sending_message_id)
    )

    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("start_sending_message:"))
async def process_time_selection(callback_query: types.CallbackQuery, state: FSMContext):
    sending_message_id = callback_query.data.split(":")[1]
    await callback_query.message.answer(
        text=f"✅Xabar yuborilishni boshladi."
    )
    sending_message_data = await db.select_message(id=int(sending_message_id))
    print("="*20)
    print(sending_message_data)
    print("="*20)

    await send_to_all_groups_with_scheduled(
        telegram_id=callback_query.from_user.id,
        message_text=sending_message_data.get("message_text"),
        message_id=int(sending_message_data.get("message_id")),
        sending_interval=timedelta(
            minutes=sending_message_data.get("sending_interval"))
    )
    await callback_query.message.answer(
        text="Asosiy menyu",
        reply_markup=main_menu_button
    )

# @dp.message_handler(state=SendingMessageState.message_text)
# async def send_message_to_groups(message: types.Message, state: FSMContext):
#     # telegram_id = message.from_user.id
#     text = message.text.strip()
#     # await message.delete()
#     if not text:
#         await message.answer(
#             text="Iltimos, yuboriladigan xabar matnini kiriting.",
#             reply_markup=back_button
#         )
#         return
#     await state.update_data(message_text=text)
#     # await send_to_all_groups(telegram_id, text)
#     # await send_to_all_groups_with_scheduled(telegram_id, text)
#     await message.answer(
#         text="⚡️Xabarlar yuborilish oralig'ini quyidan tanglang(minutda):",
#         reply_markup=time_between_messages
#     )
#     await SendingMessageState.time_between_messages.set()
