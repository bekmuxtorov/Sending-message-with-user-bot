
from telethon.tl.types import PeerChannel
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.types import DialogFilter
import asyncio

from .connect_progress import get_client
from data.config import FILTER_NAME, UZ_TIMEZONE, SENDING_COUNT, SAVE_GROUP_ID

from telethon import functions


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


async def _resolve_from_peer(client, *, channel_id: int = None, username_or_link: str = None):
    # 1) Agar username yoki t.me link bo'lsa, to'g'ridan-to'g'ri
    if username_or_link:
        try:
            return await client.get_input_entity(username_or_link)
        except Exception:
            pass  # fallbackga o'tamiz

    # 2) Dialoglarni yuklab, id bo'yicha qidiramiz (access_hash shu yerda keshga tushadi)
    #    Eslatma: klient manba kanalga a'zo bo'lishi shart.
    async for dialog in client.iter_dialogs():
        ent = dialog.entity
        if getattr(ent, 'id', None) == channel_id:
            return await client.get_input_entity(ent)

    return None  # topilmadi


async def get_from_peer(client):
    return await _resolve_from_peer(
        client,
        channel_id=3064646744,
        username_or_link="https://t.me/connection_logs/"
    )


async def send_to_all_groups_with_scheduled(telegram_id, message_text: str, message_id, sending_interval):
    client = await get_client(telegram_id, for_send_message=True)
    results = await get_ids_by_filter_name(telegram_id, FILTER_NAME, client)

    await client.disconnect()

    times_local = await setup_schedular(sending_interval)
    times_utc = [t.astimezone(timezone.utc) for t in times_local]

    await client.connect()
    from_peer = await get_from_peer(client)
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
                # from_peer = PeerChannel(channel_id=SAVE_GROUP_ID)
                # from_peer = await client.get_input_entity(PeerChannel(channel_id=3064646744))

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

    for i in range(SENDING_COUNT):
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


# async def delete_scheduled_forward(telegram_id, message_id):
#     client = await get_client(telegram_id, for_send_message=True)
#     results = await get_ids_by_filter_name(telegram_id, FILTER_NAME, client)

#     await client.disconnect()
#     await client.connect()

#     # Peer ni normalize qilish
#     # from_entity = await client.get_input_entity(from_peer)
#     from_peer = await get_from_peer(client)
#     message = await client.get_messages(telegram_id, ids=message_id)
#     message_text = message.text
#     for entity in results:
#         try:
#             scheduled = await client.get_messages(entity, scheduled=True)

#             # Forward xabarni aniq topish
#             for msg in scheduled:
#                 print("="*10)
#                 print(msg.message)
#                 print('-'*4)
#                 print(message_id)
#                 print("="*10)
#                 if (
#                     msg.fwd_from
#                     # faqat kanaldan forward bo‘lgan xabarlar
#                     and isinstance(msg.fwd_from.from_id, PeerChannel)
#                     and msg.fwd_from.from_id.channel_id == from_peer.channel_id
#                     and msg.fwd_from.channel_post == message_id
#                 ):
#                     await client.delete_messages(entity, [msg.id], revoke=True)
#                     print(
#                         f"🗑 {entity} dagi forward {message_id} scheduled o‘chirildi")
#                     break
#             else:
#                 print(f"ℹ️ {entity} da {message_id} forward scheduled topilmadi")

#         except Exception as e:
#             print(f"❌ Xatolik: {entity} => {e}")

#     await client.disconnect()
async def delete_scheduled_forward(telegram_id, message_text):
    client = await get_client(telegram_id, for_send_message=True)
    try:
        results = await get_ids_by_filter_name(telegram_id, FILTER_NAME, client)
        await client.connect()
        for entity in results:
            delete_message_ids = list()

            try:
                # scheduled_msgs = await client.get_messages(entity, scheduled=True)
                # scheduled_msgs = await client(functions.messages.GetScheduledHistoryRequest(
                #     peer=await client.get_input_entity(entity),
                #     hash=0
                # ))
                peer = await client.get_input_entity(entity)
                resp = await client(functions.messages.GetScheduledHistoryRequest(
                    peer=peer,
                    hash=0
                ))
                scheduled_msgs = getattr(resp, "messages", [])
                if not scheduled_msgs:
                    print(f"ℹ️ {entity} da scheduled xabar yo‘q")
                    continue

                for msg in scheduled_msgs:
                    if (msg.message or "").strip() == message_text.strip():
                        delete_message_ids.append(msg.id)

                await client(functions.messages.DeleteScheduledMessagesRequest(
                    peer=entity,
                    id=delete_message_ids
                ))
            except Exception as e:
                print(f"❌ {entity} ni tekshirishda xato: {e}")

    finally:
        await client.disconnect()


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
