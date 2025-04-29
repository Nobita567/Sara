from pyrogram import Client
from pyrogram.types import ChatMemberUpdated
from AudifyMusic.utils.database import add_served_chat

# no filters.my_chat_member() here—use the specialized decorator
@Client.on_chat_member_updated
async def auto_register_chat(client: Client, update: ChatMemberUpdated):
    """
    Whenever *this bot* is added to a new group (left/kicked → member/admin),
    immediately persist that chat_id so broadcasts include it—even without /start.
    """
    # Only proceed if the update concerns *this* bot
    me = await client.get_me()
    if update.new_chat_member.user.id != me.id:
        return

    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    # detect join event
    if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
        await add_served_chat(update.chat.id)
