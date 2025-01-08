from enum import Enum


class Units(Enum):
    metric = "metric"
    imperial = "imperial"


class CallbackData:
    location = "location"
    settings = "settings"
    donation = "donation"


class CallbackSettingsData:
    units_imperial = "units_imperial"
    units_metric = "units_metric"


unit_values = {
    "temp": {"metric": "℃", "imperial": "℉"},
    "wind": {"metric": "m/s", "imperial": "mi/h"},
    "grnd_level": {"metric": "hPa", "imperial": "hPa"},
    "humidity": {
        "metric": "%",
        "imperial": "%",
    },
}

cardinal_directions = {
    0: "north",
    1: "north-east",
    2: "east",
    3: "south-east",
    4: "south",
    5: "south-west",
    6: "west",
    7: "north-west",
}
