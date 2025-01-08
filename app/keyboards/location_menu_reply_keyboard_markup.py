from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


location_button = KeyboardButton(text="📍 Share my location", request_location=True)

location_menu_reply_keyboard_markup = ReplyKeyboardMarkup(
    keyboard=[[location_button]], resize_keyboard=True, one_time_keyboard=True
)
