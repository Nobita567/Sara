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

# make sure broadcast and auto-register handlers are imported early
import AudifyMusic.plugins.misc.broadcast
import AudifyMusic.plugins.misc.auto_register
from AudifyMusic.plugins.misc.broadcast import auto_clean

# AudifyMusic/__main__.py (near the top, after imports)
import AudifyMusic.plugins.misc.auto_register


async def init():
    # ─── 1) validate assistant session strings ─────────────────────────────
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error(
            "Assistant client variables not defined, exiting..."
        )
        exit()

    # ─── 2) load sudoers and bans ────────────────────────────────────────────
    await sudo()
    try:
        for uid in await get_gbanned():
            BANNED_USERS.add(uid)
        for uid in await get_banned_users():
            BANNED_USERS.add(uid)
    except:
        pass

    # ─── 3) start main bot and background tasks ─────────────────────────────
    await app.start()
    # schedule your auto_clean task now that the loop exists
    asyncio.create_task(auto_clean())

    # dynamically import all plugin modules
    for module in ALL_MODULES:
        importlib.import_module("AudifyMusic.plugins" + module)
    LOGGER("AudifyMusic.plugins").info("Successfully Imported Modules...")

    # ─── 4) start userbot and call core ────────────────────────────────────
    await userbot.start()
    await Audify.start()

    # attempt to start a dummy stream so PyTgCalls is initialized
    try:
        await Audify.stream_call(
            "https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("AudifyMusic").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit()
    except:
        pass

    # finish setting up decorators, etc.
    await Audify.decorators()
    LOGGER("AudifyMusic").info(
        "Audify Music Bot Started Successfully.\n\nDon't forget to visit @GrayBots"
    )

    # ─── 5) block here until CTRL+C ──────────────────────────────────────────
    await idle()

    # ─── 6) clean shutdown ─────────────────────────────────────────────────
    await app.stop()
    await userbot.stop()
    LOGGER("AudifyMusic").info("Stopping Audify Music Bot...")


if __name__ == "__main__":
    # old-school style: uses existing init() without top-level awaits
    asyncio.get_event_loop().run_until_complete(init())
