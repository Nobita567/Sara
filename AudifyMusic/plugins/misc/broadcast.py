import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from AudifyMusic import app
from AudifyMusic.misc import SUDOERS
from AudifyMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from AudifyMusic.utils.decorators.language import language
from AudifyMusic.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False

@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def broadcast_message(client, message, _):
    global IS_BROADCASTING

    # 1) Determine payload: reply (forward) vs plain text
    if message.reply_to_message:
        to_forward_id = message.reply_to_message.id
        source_chat   = message.chat.id
        query_text    = None
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        raw = message.text.split(None, 1)[1]
        for flag in ("-pin", "-pinloud", "-nobot", "-assistant", "-user"):
            raw = raw.replace(flag, "")
        query_text = raw.strip()
        if not query_text:
            return await message.reply_text(_["broad_8"])
        to_forward_id = None
        source_chat   = None

    # 2) Parse flags
    txt = message.text.lower()
    flags = {
        "nobot":     "-nobot"     in txt,
        "pin":       "-pin"       in txt,
        "pinloud":   "-pinloud"   in txt,
        "user":      "-user"      in txt,
        "assistant": "-assistant" in txt,
    }

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # 3a) Bot-level broadcast
    if not flags["nobot"]:
        sent, pinned = 0, 0
        schats = await get_served_chats()
        for row in schats:
            cid = int(row["chat_id"])
            try:
                m = (await app.forward_messages(cid, source_chat, to_forward_id)) \
                    if to_forward_id \
                    else await app.send_message(cid, query_text)

                if flags["pin"]:
                    await m.pin(disable_notification=True); pinned += 1
                elif flags["pinloud"]:
                    await m.pin(disable_notification=False); pinned += 1

                sent += 1
                await asyncio.sleep(0.2)

            except FloodWait as fw:
                await asyncio.sleep(min(int(fw.value), 200))
            except:
                continue

        await message.reply_text(_["broad_3"].format(sent, pinned))

    # 3b) User-level broadcast
    if flags["user"]:
        ucount = 0
        for row in await get_served_users():
            uid = int(row["user_id"])
            try:
                if to_forward_id:
                    await app.forward_messages(uid, source_chat, to_forward_id)
                else:
                    await app.send_message(uid, query_text)
                ucount += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                await asyncio.sleep(min(int(fw.value), 200))
            except:
                continue

        await message.reply_text(_["broad_4"].format(ucount))

    # 3c) Assistant-level broadcast
    if flags["assistant"]:
        report     = _["broad_6"]
        status_msg = await message.reply_text(_["broad_5"])
        from AudifyMusic.core.userbot import assistants

        for num in assistants:
            a_sent   = 0
            client2  = await get_client(num)
            async for dialog in client2.get_dialogs():
                try:
                    if to_forward_id:
                        await client2.forward_messages(dialog.chat.id, source_chat, to_forward_id)
                    else:
                        await client2.send_message(dialog.chat.id, query_text)
                    a_sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    await asyncio.sleep(min(int(fw.value), 200))
                except:
                    continue

            report += _["broad_7"].format(num, a_sent)

        await status_msg.edit_text(report)

    IS_BROADCASTING = False


async def auto_clean():
    while True:
        await asyncio.sleep(10)
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    for u in await get_authuser_names(chat_id):
                        uid = await alpha_to_int(u)
                        adminlist[chat_id].append(uid)
        except:
            pass

# start background cleaner
asyncio.create_task(auto_clean())
