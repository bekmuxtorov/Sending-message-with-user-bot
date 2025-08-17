from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

from data.config import API_ID, API_HASH
import os


def init_db(database):
    global db
    db = database


async def create_client(telegram_id: int):
    os.makedirs("sessions", exist_ok=True)
    session_path = os.path.join("sessions", f"session_{telegram_id}")
    client = TelegramClient(session_path, API_ID, API_HASH)
    return client


async def get_session_path(telegram_id: int) -> str:
    os.makedirs("sessions", exist_ok=True)
    return os.path.join("sessions", f"session_{telegram_id}")


async def send_code_for_create_session(telegram_id: str, phone_number: str) -> str:
    client = await create_client(telegram_id)
    await client.connect()

    if not await client.is_user_authorized():
        sent = await client.send_code_request(phone_number)
        phone_code_hash = sent.phone_code_hash
    else:
        phone_code_hash = None

    await client.disconnect()
    return phone_code_hash


async def verify_code_and_sign_in(telegram_id: str, phone_number: str, code: str, phone_code_hash: str) -> bool:
    session_path = await get_session_path(telegram_id)
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()
    if not phone_code_hash:
        raise ValueError(
            "phone_code_hash topilmadi. Avval send_code_request ishlating.")

    try:
        await client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)
        await db.add_session(telegram_id, session_path)
        return True
    except SessionPasswordNeededError:
        return False
    finally:
        await client.disconnect()


async def sign_in_with_2fa(telegram_id: str, password: str) -> None:
    session_path = await get_session_path(telegram_id)
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    try:
        await client.sign_in(password=password)
        await db.add_session(telegram_id, session_path)
    finally:
        await client.disconnect()


# ========== String Session Functions ==========
async def send_code_for_create_string_session(telegram_id: str, phone_number: str) -> str:
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    string_session = client.session.save()
    print(string_session)
    await db.add_session(telegram_id, string_session)
    print(f"String session for {telegram_id} created: {string_session}")
    await client.connect()

    if not await client.is_user_authorized():
        sent = await client.send_code_request(phone_number)
        phone_code_hash = sent.phone_code_hash
    else:
        phone_code_hash = None

    await client.disconnect()
    return phone_code_hash


async def verify_code_and_sign_in_with_string_session(telegram_id: str, phone_number: str, code: str, phone_code_hash: str) -> bool:
    string_session = await db.select_only_session_data(user_id=telegram_id)
    client = TelegramClient(string_session, API_ID, API_HASH)
    await client.connect()
    if not phone_code_hash:
        raise ValueError(
            "phone_code_hash topilmadi. Avval send_code_request ishlating.")

    try:
        await client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)
        return True
    except SessionPasswordNeededError:
        return False
    finally:
        await client.disconnect()


async def sign_in_with_2fa_with_string_session(telegram_id: str, password: str) -> None:
    string_session = await db.select_only_session_data(user_id=telegram_id)
    client = TelegramClient(string_session, API_ID, API_HASH)
    await client.connect()

    try:
        await client.sign_in(password=password)
    finally:
        await client.disconnect()
