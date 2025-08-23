from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from keyboards.inline.inline_buttons import done_button, main_menu_button, generate_time_keyboard
from utils.using_folders import get_ids_by_filter_name, send_to_all_groups, send_to_all_groups_with_scheduled
from states.sending_message import SendingMessageSchedularState
from keyboards.default.default_buttons import back_button


@dp.callback_query_handler(text="sending_message_in_another_time")
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        text="Xabar yuborish uchun yubormoqchi bo'lgan guruhlaringizni barchasini bir guruhga ya'ni Avto papkasiga yig'ing. Bu bo'yicha yuqorida video ko'rsatma yuborildi.",
        reply_markup=done_button
    )
    await SendingMessageSchedularState.done.set()


@dp.callback_query_handler(text="done", state=SendingMessageSchedularState.done)
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
        text="Guruhlarga xabarni yuborilish vaqtlarini quyidan tanglang:",
        reply_markup=generate_time_keyboard()
    )
    await SendingMessageSchedularState.message_text.set()


@dp.message_handler(state=SendingMessageSchedularState.message_text)
async def send_message_to_groups(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    text = message.text.strip()
    await message.delete()
    if not text:
        await message.answer(
            text="Iltimos, yuboriladigan xabar matnini kiriting.",
            reply_markup=back_button
        )
        return
    await send_to_all_groups(telegram_id, text)
    # await send_to_all_groups_with_scheduled(telegram_id, text)
    await message.answer(
        text="Xabar barcha guruhlarga yuborildi.",
        reply_markup=main_menu_button
    )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("time_"))
async def process_time_selection(callback_query: types.CallbackQuery):
    selected_time = callback_query.data.replace("time_", "")

    # Eski matnga yangi vaqtni qo‘shib boramiz
    old_text = callback_query.message.text
    if "Tanlangan vaqtlar:" not in old_text:
        new_text = f"Tanlangan vaqtlar:\n- {selected_time}"
    else:
        new_text = old_text + f"\n- {selected_time}"

    await callback_query.message.edit_text(new_text, reply_markup=generate_time_keyboard())
    await callback_query.answer(f"{selected_time} qo‘shildi ✅")
