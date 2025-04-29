from pyrogram import filters
from pyrogram.types import ChatMemberUpdated
from AudifyMusic import app
from AudifyMusic.utils.database import add_served_chat

@app.on_chat_member_updated(filters.my_chat_member())
async def auto_register_chat(client, update: ChatMemberUpdated):
    """
    When the bot itself is added to a chat (left → member/admin),
    persist that chat_id so broadcasts include it automatically.
    """
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    # Only trigger on actual join
    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
        await add_served_chat(update.chat.id)
