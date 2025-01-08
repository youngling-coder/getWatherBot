import aiohttp
from settings import settings
from custom_types import Units, unit_values, cardinal_directions
from typing import Tuple
import flag


class WeatherHandler:
    def __init__(self):
        self.__appid = settings.open_weather_api_token

    def __prettify_output(
        self, data: dict, place: str, units: str = Units.metric.value
    ) -> str:

        cardinal_directions_amount = len(cardinal_directions.keys())
        wind_direction = data["wind"]["deg"] + ((360 / cardinal_directions_amount) / 2)

        if wind_direction > 360:
            wind_direction = wind_direction - 360

        wind_direction //= 45

        base_template = f"""
✅ Requested weather in ***{place}***:

***📄Summary:*** {data['weather'][0]['description'].capitalize()}
***🌡 Temperature:*** {data['main']['temp']}{unit_values['temp'][units]} (feels like {data['main']['feels_like']}{unit_values['temp'][units]})
***💨 Wind:*** {data['wind']['speed']}{unit_values['wind'][units]}, 🧭 {cardinal_directions[wind_direction].capitalize()}
***⛓️ Pressure:*** {data['main']['grnd_level']} {unit_values['grnd_level'][units]}
***💧Humidity:*** {data['main']['humidity']}{unit_values['humidity'][units]}

***✨ Have a nice day!***
"""

        return base_template

    async def __handle_request(self, url: str, session: aiohttp.ClientSession):

        async with session.get(url) as response:

            if response.status == 200:
                data = await response.json()

                return data
            else:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=response.text,
                )

    async def __to_location(self, session: aiohttp.ClientSession, place: str) -> dict:

        url = settings.geocoding_url
        url = f"{url}?q={place}&appid={self.__appid}"

        data = await self.__handle_request(url, session)

        if data:
            location_data = data[0]
            return location_data

        raise ValueError(f"No location found for place {place}")

    async def __obtain_weather_info(
        self, location: Tuple[int, int], units: str = Units.metric.value
    ):

        url = settings.open_weather_url
        url = f"{url}?lat={location[0]}&lon={location[1]}&units={units}&appid={self.__appid}"

        async with aiohttp.ClientSession() as session:

            data = await self.__handle_request(url, session)

            return data

    async def get_weather_from_location(
        self, location: Tuple[int, int], units=Units.metric.value
    ):

        async with aiohttp.ClientSession() as session:

            place = f"{location[0]}, {location[1]}"
            weather = await self.__obtain_weather_info(location=location, units=units)
            return self.__prettify_output(weather, place, units=units)

    async def get_weather_from_place(
        self, place: str, units: str = Units.metric.value
    ) -> str:

        async with aiohttp.ClientSession() as session:

            location_data = await self.__to_location(session=session, place=place)
            location = (location_data["lat"], location_data["lon"])
            place = f"{flag.flag(location_data['country'])} {location_data['name']},"

            if location_data.get("state"):
                place += f" {location_data['state']},"

            place += f" {location_data['country']}"
            weather = await self.__obtain_weather_info(location=location, units=units)
            return self.__prettify_output(weather, place, units=units)
