from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str

    telegram_bot_token: str
    open_weather_api_token: str
    open_weather_url: str
    geocoding_url: str

    class Config:
        env_file = ".env"


settings = Settings()
