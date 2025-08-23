from aiogram.dispatcher.filters.state import State, StatesGroup


class CheckPayment(StatesGroup):
    send_invoice = State()
