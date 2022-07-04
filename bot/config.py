from typing import Dict
from dotenv import dotenv_values
from pydantic import BaseModel
import pydantic


class _EnvironmentVariables(BaseModel):
    ENVIRONMENT: str
    GEMINI_TRADING_API_KEY: str
    GEMINI_TRADING_API_SECRET: str
    SQL_DATABASE_CONNECTION_STRING: str
    SQL_DATABASE: str
    SQL_USERNAME: str
    SQL_PASSWORD: str


try:
    _env_values: _EnvironmentVariables = _EnvironmentVariables(**dotenv_values())
except pydantic.error_wrappers.ValidationError as e:
    raise ValueError(
        "Please create a .env file with the correct environment variables"
    ) from e

environment: str = _env_values.ENVIRONMENT
database: str = _env_values.SQL_DATABASE
database_connection_string: str = _env_values.SQL_DATABASE_CONNECTION_STRING

stop_limit_step: Dict[str, float] = {"SGD": 50, "ETH": 0.01, "BTC": 0.001}
dca_amount: float = 2  # in token_b_value
reserved_amount_for_market_orders: Dict[str, float] = {"SGD": 500}
max_limit_order_price: Dict[str, float] = {"ETHSGD": 2000}
min_limit_order_price: Dict[str, float] = {"ETHSGD": 5}
hours_to_pass_per_market_order: float = 1.5
max_tkn_b_market_price_in_tkn_a: float = 2000
market_order_price_percentage_delta_to_highest_limit_order: float = 1.05
market_order_price_percentage_delta_to_last_trade_price: float = 1.2
market_order_aggressiveness_factor: float = 1.3
automatic_stop_limit_price_steps_for_buying_dip = 50  # in token_b_value
client_order_id = "rx_trading_bot"
