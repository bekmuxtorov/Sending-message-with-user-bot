from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from keyboards.inline.inline_buttons import start_button
from states.setting_bots import SettingsBot


@dp.callback_query_handler(text="start_button")
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        text="Yaxshi. Botni sozlash boshlandi.\n\nUlamoqchi bo'lgan akkauntingizni telefon raqamini quyiga +998901234567 ko'rinishida yuboring:",
    )
    await SettingsBot.phone_number.set()


@dp.callback_query_handler(state=SettingsBot.phone_number)
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    phone_number = call.message.text
    if not phone_number.startswith("+998") or len(phone_number) != 13:
        await call.message.answer(
            text="Iltimos, telefon raqamingizni to'g'ri formatda yuboring: +998901234567"
        )
        return
    await call.message.delete()

    await call.message.answer(
        text="Telegram orqali yuborilgan kodni quyiga kiriting.",
    )
    await state.update_data(phone_number=phone_number)
    await SettingsBot.code_from_telegram.set()
