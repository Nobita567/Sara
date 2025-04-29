import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AudifyMusic import LOGGER, app, userbot
from AudifyMusic.core.call import Audify
from AudifyMusic.misc import sudo
from AudifyMusic.plugins import ALL_MODULES
from AudifyMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

# import misc plugins so they register on startup
import AudifyMusic.plugins.misc.broadcast
import AudifyMusic.plugins.misc.auto_register

async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("AudifyMusic.plugins" + all_module)
    LOGGER("AudifyMusic.plugins").info("Successfully Imported Modules...")
from AudifyMusic.plugins.misc.broadcast import auto_clean

async def main():
    asyncio.create_task(auto_clean())  # run in background
    await userbot.start()              # your userbot start logic here
    await idle()                       # keep the bot running

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

    await userbot.start()
    await Audify.start()

    await userbot.start()
    await Audify.start()
    try:
        await Audify.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("AudifyMusic").error(
            "Please turn on the videochat of your log group\channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass
    await Audify.decorators()
    LOGGER("AudifyMusic").info(
        "Audify Music Bot Started Successfully.\n\nDon't forget to visit @GrayBots"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("AudifyMusic").info("Stopping Audify Music Bot...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
