import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

import models
from database import get_db
from settings import settings
from services import WeatherHandler
from custom_types import CallbackData, Units, CallbackSettingsData
from keyboards import (
    main_menu_inline_keyboard_markup,
    location_menu_reply_keyboard_markup,
)


TOKEN = settings.telegram_bot_token

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))

dp = Dispatcher()
wh = WeatherHandler()


@dp.callback_query(F.data.startswith("units"))
async def update_units(callback_query: types.CallbackQuery):

    if Units.metric.value in callback_query.data:
        units = Units.metric.value
    else:
        units = Units.imperial.value

    async for db in get_db():
        stmt = (
            update(models.User)
            .where(models.User.telegram_id == callback_query.from_user.id)
            .values(units=units)
        )
        await db.execute(stmt)
        await db.commit()

    await callback_query.message.edit_text(
        text=f"✅ You are now using ***{units}*** units!",
        reply_markup=main_menu_inline_keyboard_markup,
    )


@dp.callback_query()
async def process_callback_query(callback_query: types.CallbackQuery):

    data = callback_query.data

    async for db in get_db():

        stmt = select(models.User).filter(
            models.User.telegram_id == callback_query.from_user.id
        )
        result = await db.execute(stmt)
        user = result.scalars().first()

    if data == CallbackData.location:
        await bot.send_message(
            callback_query.from_user.id,
            text="📍Press the button below to share your location",
            reply_markup=location_menu_reply_keyboard_markup,
        )

    elif data == CallbackData.settings or data.startswith("settings"):
        units = Units.metric.value

        if user:
            units = user.units.value

            imperial_text = "🇺🇸 Imperial"
            metric_text = "🇪🇺 Metric"

            if units == Units.metric.value:
                metric_text = "✅ Metric"
            else:
                imperial_text = "✅ Imperial"

            metric_button = types.InlineKeyboardButton(
                text=metric_text, callback_data=CallbackSettingsData.units_metric
            )
            imperial_button = types.InlineKeyboardButton(
                text=imperial_text, callback_data=CallbackSettingsData.units_imperial
            )

            settings_menu_inline_keyboard_markup = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [metric_button, imperial_button],
                ]
            )

            await callback_query.message.edit_text(
                text="***📏 Update preferable units***",
                reply_markup=settings_menu_inline_keyboard_markup,
            )

    elif data.startswith("donation"):
        await bot.send_message(
            callback_query.from_user.id,
            text=f"🙏 Thank you for considering a donation!",
        )


@dp.message(CommandStart())
async def start_command_handler(message: types.Message) -> None:

    async for db in get_db():
        stmt = select(models.User).filter(
            models.User.telegram_id == message.from_user.id
        )
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user:
            new_user = models.User(telegram_id=message.from_user.id)
            db.add(new_user)
            await db.commit()

    message_text = f"""
***🌞 Hello, {message.from_user.full_name}!***

Send me any city, country, or village – or just share your location!
I'll get the weather for you in no time. 😊
"""

    await message.answer(
        message_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_inline_keyboard_markup,
    )


@dp.message()
async def get_user_input(message: types.Message):

    units = Units.metric.value

    async for db in get_db():
        stmt = select(models.User).filter(
            models.User.telegram_id == message.from_user.id
        )
        result = await db.execute(stmt)
        user = result.scalars().first()

    if user:
        units = user.units.value

    try:
        if message.location:
            location = (message.location.latitude, message.location.longitude)

            weather = await wh.get_weather_from_location(location=location, units=units)

        else:
            weather = await wh.get_weather_from_place(place=message.text, units=units)

        await message.reply(text=weather, parse_mode=ParseMode.MARKDOWN)

    except Exception as ex:

        message_text = f"""
❌ I'm sorry, but I couldn't process your request!

***💁‍♂️ This may help:***
  - Check your spelling
  - Repeat your query
  - Try again later
"""
        await message.reply(text=message_text, parse_mode=ParseMode.MARKDOWN)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
