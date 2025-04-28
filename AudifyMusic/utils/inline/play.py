import math
from pyrogram.types import InlineKeyboardButton
from AudifyMusic.utils.formatters import time_to_seconds

def get_progress_bar(percentage):
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        return "▰▱▱▱▱▱▱▱▱"
    elif 10 < umm <= 20:
        return "▰▰▱▱▱▱▱▱▱"
    elif 20 < umm <= 30:
        return "▰▰▰▱▱▱▱▱▱"
    elif 30 < umm <= 40:
        return "▰▰▰▰▱▱▱▱▱"
    elif 40 < umm <= 50:
        return "▰▰▰▰▰▱▱▱▱"
    elif 50 < umm <= 60:
        return "▰▰▰▰▰▰▱▱▱"
    elif 60 < umm <= 70:
        return "▰▰▰▰▰▰▰▱▱"
    elif 70 < umm <= 80:
        return "▰▰▰▰▰▰▰▰▱"
    elif 80 < umm <= 90:
        return "▰▰▰▰▰▰▰▰▰"
    elif 90 < umm <= 100:
        return "▰▰▰▰▰▰▰▰▰▰"
    else:
        return "▱▱▱▱▱▱▱▱▱"

def stream_markup_timer(_, videoid, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    bar = get_progress_bar(percentage)
    buttons = [
        [InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [
            InlineKeyboardButton(text=_["P_B_7"], callback_data=f"add_playlist {videoid}"),
            InlineKeyboardButton(text=_["PL_B_3"], callback_data=f"PanelMarkup {videoid}|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")],
    ]
    return buttons

def stream_markup(_, videoid, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text=_["P_B_7"], callback_data=f"add_playlist {videoid}"),
            InlineKeyboardButton(text=_["PL_B_3"], callback_data=f"PanelMarkup None|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")],
    ]
    return buttons

def telegram_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    bar = get_progress_bar(percentage)
    buttons = [
        [InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")],
        [InlineKeyboardButton(text=_["PL_B_3"], callback_data=f"PanelMarkup None|{chat_id}")],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")],
    ]
    return buttons

def telegram_markup(_, chat_id):
    buttons = [
        [InlineKeyboardButton(text=_["PL_B_3"], callback_data=f"PanelMarkup None|{chat_id}")],
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text=_["CLOSEMENU_BUTTON"], callback_data="close")],
    ]
    return buttons

# (…and so on for track_markup, playlist_markup, livestream_markup, slider_markup, panel_markup_1/2/3)
