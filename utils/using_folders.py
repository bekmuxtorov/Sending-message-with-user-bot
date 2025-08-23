
from telethon.tl.types import PeerChannel
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.types import DialogFilter, InputPeerChannel, InputPeerUser, InputPeerChat
import asyncio

from .connect_progress import get_client
from data.config import FILTER_NAME, UZ_TIMEZONE, SAVE_GROUP_ID


async def get_timezone():
    return ZoneInfo(UZ_TIMEZONE)


async def get_ids_by_filter_name(telegram_id, filter_name=FILTER_NAME, client=None):
    if not client:
        client = await get_client(telegram_id, for_send_message=True)

    result = await client(GetDialogFiltersRequest())
    await client.disconnect()

    peers = []

    for f in result.filters:
        if isinstance(f, DialogFilter) and f.title.text == filter_name:
            peers.extend(f.pinned_peers + f.include_peers)

    # clean_peers = [p for p in peers if not isinstance(p, InputPeerUser)]

    return peers


async def send_to_all_groups(telegram_id, message_text: str):
    client = await get_client(telegram_id, for_send_message=True)
    results = await get_ids_by_filter_name(telegram_id, FILTER_NAME, client)

    await client.disconnect()

    await client.connect()
    for entity in results:
        try:
            print(f"Yuborilmoqda: {entity}")
            await client.send_message(entity, message_text)
            print(f"✅ Yuborildi: {entity}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Xatolik: {entity} => {e}")

    await client.disconnect()


async def send_to_all_groups_with_scheduled(telegram_id, message_text: str, message_id, sending_interval):
    client = await get_client(telegram_id, for_send_message=True)
    results = await get_ids_by_filter_name(telegram_id, FILTER_NAME, client)

    await client.disconnect()

    times_local = await setup_schedular(sending_interval)
    times_utc = [t.astimezone(timezone.utc) for t in times_local]

    await client.connect()

    for entity in results:
        try:
            now_utc = datetime.now(timezone.utc)
            safe_times = [t if t > now_utc + timedelta(seconds=30)
                          else now_utc + timedelta(minutes=1)
                          for t in times_utc]

            print(f"Yuborilmoqda: {entity}")
            for t in safe_times:
                # await client.send_message(
                #     entity,
                #     message_text,
                #     schedule=t
                # )
                # await client.copy_message(
                #     entity,                # qaysi guruhga yuborish kerak
                #     messages=55554,        # manba xabar ID
                #     from_peer=44444,       # manba guruh ID
                #     schedule_date=t
                # )
                from_peer = PeerChannel(channel_id=3064646744)
                await client.forward_messages(
                    entity=entity,
                    messages=message_id,
                    from_peer=from_peer,
                    schedule=t,          # rejalashtirish vaqti (UTC)
                )
            scheduled = await client.get_messages(entity, scheduled=True)
            print("📅 Scheduled:", [m.date for m in scheduled])
            await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ Xatolik: {entity} => {e}")

    await client.disconnect()


async def setup_schedular(sending_interval: timedelta):
    UZ = await get_timezone()
    now_local = datetime.now(UZ)
    times_local = []

    for i in range(6):
        next_time = now_local + sending_interval * (i + 1)

        if next_time.date() != now_local.date():
            next_time = datetime.combine(
                now_local.date() + timedelta(days=1),
                next_time.timetz(),
                tzinfo=UZ
            )

        times_local.append(next_time)

    times_utc = [t.astimezone(timezone.utc) for t in times_local]
    return times_utc


# async def get_ids_by_filter_name(telegram_id, filter_name=FILTER_NAME, client=None):
#     if not client:
#         client = await get_client(telegram_id, for_send_message=True)

#     result = await client(GetDialogFiltersRequest())
#     client.disconnect()
#     ids = []

#     for f in result.filters:
#         if isinstance(f, DialogFilter) and f.title.text == filter_name:
#             peers = f.pinned_peers + f.include_peers
#             for p in peers:
#                 if isinstance(p, InputPeerChannel):
#                     ids.append(p.channel_id)
#                 elif isinstance(p, InputPeerUser):
#                     ids.append(p.user_id)
#                 elif isinstance(p, InputPeerChat):
#                     ids.append(p.chat_id)
#     return ids

# async def send_to_all_groups(telegram_id, message_text: str):
#     client = await get_client(telegram_id, for_send_message=True)
#     results = await get_ids_by_filter_name(telegram_id, FILTER_NAME, client)
#     print("9" * 20)
#     print(f"Yuboriladigan guruhlar: {results}")
#     print("9" * 20)
#     await client.disconnect()

#     await client.connect()
#     for chat_id in results:
#         try:
#             print(f"Yuborilmoqda: {chat_id}")
#             # entity = await client.get_input_entity(chat_id)
#             entity = await client.get_entity(chat_id)
#             await client.send_message(entity, message_text)
#             # await client.send_message(entity, message_text)
#             print(f"✅ Yuborildi: {chat_id}")

#             await asyncio.sleep(2)
#         except Exception as e:
#             print(f"❌ Xatolik: {chat_id} => {e}")
#     await client.disconnect()


# QARA SEN MENI KUZATIB TURGAN BO'LSANG MEN SENI TOPAMAN, VA TAVBANGGA TAYANTIRAMAN, SICHQONCHANI YURGIZGANINGDA BILINIB QOVVOTI, BILDIRMASDAN KUZATDA QO'CHQOR.
# ALOQADAMIZ
