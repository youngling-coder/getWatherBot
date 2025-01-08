from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from custom_types import CallbackData

settings_button = InlineKeyboardButton(
    text="⚙️ Settings", callback_data=CallbackData.settings
)
location_button = InlineKeyboardButton(
    text="🗺 Weather via location", callback_data=CallbackData.location
)
donate_button = InlineKeyboardButton(
    text="💰 Make a donation", callback_data=CallbackData.donation
)

main_menu_inline_keyboard_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [location_button],
        [settings_button, donate_button],
    ]
)
