from dotenv import dotenv_values
from pydantic import BaseModel
from bot.utils import dotenv_path


class GeminiCredentials(BaseModel):
    api_key: str
    api_secret: str


def load_credentials() -> GeminiCredentials:
    env_values = dotenv_values(dotenv_path)
    trader_credentials = GeminiCredentials(
        api_key=env_values["GEMINI_TRADING_API_KEY"],
        api_secret=env_values["GEMINI_TRADING_API_SECRET"],
    )
    return trader_credentials
