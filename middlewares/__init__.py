from aiogram import Dispatcher

from loader import dp
from .throttling import ThrottlingMiddleware
# from middlewares.payment import PaymentMiddleware


if __name__ == "middlewares":
    dp.middleware.setup(ThrottlingMiddleware())
    # dp.middleware.setup(PaymentMiddleware())
