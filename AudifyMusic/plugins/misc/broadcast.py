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
    """
    Supports two modes:
      1) Media broadcast when using -wfchat / -wfuser flags on a reply-to (photo/text).
      2) Normal broadcast: reply-to forward or plain text + flags:
           -nobot, -pin, -pinloud, -user, -assistant
    """
    global IS_BROADCASTING
    text = message.text or ""

    # ----- MODE 1: Media broadcast via -wfchat / -wfuser -----
    if "-wfchat" in text or "-wfuser" in text:
        # must be a reply-to with photo or text
        rm = message.reply_to_message
        if not rm or not (rm.photo or rm.text):
            return await message.reply_text("❌ Please reply to a text or image message for broadcasting.")

        # extract media or text
        if rm.photo:
            content_type = "photo"
            file_id = rm.photo.file_id
            caption = rm.caption or ""
        else:
            content_type = "text"
            text_content = rm.text

        reply_markup = getattr(rm, "reply_markup", None)

        IS_BROADCASTING = True
        await message.reply_text(_["broad_1"])

        # broadcast to served chats
        if "-wfchat" in text:
            sent_chats = 0
            for row in await get_served_chats():
                cid = int(row["chat_id"])
                try:
                    if content_type == "photo":
                        await app.send_photo(cid, file_id, caption=caption, reply_markup=reply_markup)
                    else:
                        await app.send_message(cid, text_content, reply_markup=reply_markup)
                    sent_chats += 1
                    await asyncio.sleep(0.2)
                except FloodWait as fw:
                    await asyncio.sleep(min(int(fw.value), 200))
                except:
                    continue
            await message.reply_text(f"✅ Broadcast to chats completed! Sent to {sent_chats} chats.")

        # broadcast to served users
        if "-wfuser" in text:
            sent_users = 0
            for row in await get_served_users():
                uid = int(row["user_id"])
                try:
                    if content_type == "photo":
                        await app.send_photo(uid, file_id, caption=caption, reply_markup=reply_markup)
                    else:
                        await app.send_message(uid, text_content, reply_markup=reply_markup)
                    sent_users += 1
                    await asyncio.sleep(0.2)
                except FloodWait as fw:
                    await asyncio.sleep(min(int(fw.value), 200))
                except:
                    continue
            await message.reply_text(f"✅ Broadcast to users completed! Sent to {sent_users} users.")

        IS_BROADCASTING = False
        return

    # ----- MODE 2: Normal broadcast -----
    # 1) determine reply-forward vs new text
    if message.reply_to_message:
        to_forward_id = message.reply_to_message.id
        source_chat   = message.chat.id
        query_text    = None
        reply_markup  = getattr(message.reply_to_message, "reply_markup", None)
    else:
        parts = message.text.split(None, 1)
        if len(parts) < 2:
            return await message.reply_text(_["broad_2"])
        raw = parts[1]
        # strip known flags from raw text
        for flag in ("-pin", "-pinloud", "-nobot", "-assistant", "-user"):
            raw = raw.replace(flag, "")
        query_text = raw.strip()
        if not query_text:
            return await message.reply_text(_["broad_8"])
        to_forward_id = None
        source_chat   = None
        reply_markup  = None

    # 2) parse flags
    txt_lower = text.lower()
    flags = {
        "nobot":     "-nobot"     in txt_lower,
        "pin":       "-pin"       in txt_lower,
        "pinloud":   "-pinloud"   in txt_lower,
        "user":      "-user"      in txt_lower,
        "assistant": "-assistant" in txt_lower,
    }

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # 3a) bot-level broadcast (served chats)
    if not flags["nobot"]:
        sent, pinned = 0, 0
        for row in await get_served_chats():
            cid = int(row["chat_id"])
            try:
                if to_forward_id:
                    m = await app.copy_message(cid, source_chat, to_forward_id, reply_markup=reply_markup)
                else:
                    m = await app.send_message(cid, query_text, reply_markup=reply_markup)

                if flags["pin"]:
                    try:
                        await m.pin(disable_notification=True)
                        pinned += 1
                    except:
                        pass
                elif flags["pinloud"]:
                    try:
                        await m.pin(disable_notification=False)
                        pinned += 1
                    except:
                        pass

                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                await asyncio.sleep(min(int(fw.value), 200))
            except:
                continue
        await message.reply_text(_["broad_3"].format(sent, pinned))

    # 3b) user-level broadcast
    if flags["user"]:
        ucount = 0
        for row in await get_served_users():
            uid = int(row["user_id"])
            try:
                if to_forward_id:
                    await app.copy_message(uid, source_chat, to_forward_id, reply_markup=reply_markup)
                else:
                    await app.send_message(uid, query_text, reply_markup=reply_markup)
                ucount += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                await asyncio.sleep(min(int(fw.value), 200))
            except:
                continue
        await message.reply_text(_["broad_4"].format(ucount))

    # 3c) assistant-level broadcast
    if flags["assistant"]:
        report     = _["broad_6"]
        status_msg = await message.reply_text(_["broad_5"])
        from AudifyMusic.core.userbot import assistants

        for num in assistants:
            a_sent  = 0
            client2 = await get_client(num)
            async for dialog in client2.get_dialogs():
                try:
                    if to_forward_id:
                        await client2.copy_message(dialog.chat.id, source_chat, to_forward_id, reply_markup=reply_markup)
                    else:
                        await client2.send_message(dialog.chat.id, query_text, reply_markup=reply_markup)
                    a_sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    await asyncio.sleep(min(int(fw.value), 200))
                except:
                    continue
            report += _["broad_7"].format(num, a_sent)

        try:
            await status_msg.edit_text(report)
        except:
            pass

    IS_BROADCASTING = False


async def auto_clean():
    while True:
        await asyncio.sleep(10)
        try:
            served = await get_active_chats()
            for chat_id in served:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for mem in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if mem.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(mem.user.id)
                    for name in await get_authuser_names(chat_id):
                        uid = await alpha_to_int(name)
                        adminlist[chat_id].append(uid)
        except:
            pass

# start the cleaner in background
asyncio.create_task(auto_clean())
