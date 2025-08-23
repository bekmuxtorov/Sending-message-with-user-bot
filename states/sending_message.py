from aiogram.dispatcher.filters.state import State, StatesGroup


class SendingMessageState(StatesGroup):
    message_text = State()
    time_between_messages = State()


class SendingMessageSchedularState(StatesGroup):
    message_text = State()
    done = State()
    schedular_time = State()
