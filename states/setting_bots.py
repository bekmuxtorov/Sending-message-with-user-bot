from aiogram.dispatcher.filters.state import State, StatesGroup


class SettingsBot(StatesGroup):
    phone_number = State()
    code_from_telegram = State()
    code_two_step_from_telegram = State()
