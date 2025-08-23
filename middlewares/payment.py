# from aiogram import types
# from aiogram.dispatcher.middlewares import BaseMiddleware
# from aiogram.dispatcher.handler import CancelHandler
# from datetime import datetime, timezone
# from zoneinfo import ZoneInfo

# from loader import db
# from data.config import UZ_TIMEZONE
# from keyboards.inline.inline_buttons import pament_inline_keyboard


# class PaymentMiddleware(BaseMiddleware):
#     """
#     Har bir xabar kelganda foydalanuvchining to‘lov holatini tekshiradi.
#     """
#     pass
# async def on_process_message(self, message: types.Message, data: dict):
#     if message.chat.type != "private":
#         return

#     user_id = message.from_user.id
#     user_data = await db.select_user(telegram_id=user_id)
#     if not user_data:
#         return

#     now = datetime.now(ZoneInfo(UZ_TIMEZONE))
#     user_register_date = user_data.get("created_at")
#     if (now - user_register_date).days <= 1:
#         return

#     record = await db.select_payment(user_id=user_id)

#     if not record or not record.get("is_paid") or record.get("end_date") < datetime.now(timezone.utc):
#         await message.answer(
#             text="❌ Sizning obunangiz faol emas.\n\nIltimos, to‘lov qiling va qayta urinib ko‘ring.",
#             reply_markup=pament_inline_keyboard
#         )
#         raise CancelHandler()
