from typing import Dict, NamedTuple
from dotenv import dotenv_values
from pydantic import BaseModel
import pydantic
from bot.models import MarketPrices


# environment variables


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

# Shared variables


class TimeIntervals(NamedTuple):
    days_in_a_month: int = 30
    hours_in_a_day: int = 24
    secs_in_a_min: int = 60
    seconds: int = 1


time_intervals = TimeIntervals()
client_order_id = "rx_trading_bot"
market_prices_cache: Dict[str, MarketPrices] = {}

# User config values
dca_budget_per_month: float = 500  # in token_b_value
dca_amount_per_transaction: float = 2.55  # in token_b_value
tkn_pair_min_order_amount: Dict[str, float] = {
    "ETHSGD": 10**-3
}  # https://docs.gemini.com/rest-api/#basis-point
stop_limit_step: Dict[str, float] = {"SGD": 50, "ETH": 0.01, "BTC": 0.001}
reserved_amount_for_market_orders: Dict[str, float] = {"SGD": 500}
limit_order_budget_per_month: float = 500  # in token_b_value
limit_order_amount_per_transaction: float = 50  # in token_b_value
max_limit_order_price: Dict[str, float] = {"ETHSGD": 2000}
min_limit_order_price: Dict[str, float] = {"ETHSGD": 5}
max_tkn_b_market_price_in_tkn_a: float = 2000
market_order_price_percentage_delta_to_highest_limit_order: float = 1.05
market_order_price_percentage_delta_to_last_trade_price: float = 1.2
market_order_aggressiveness_factor: float = 1.3
automatic_stop_limit_price_steps_for_buying_dip = 50  # in token_b_value


dca_transactions_per_day = (
    dca_budget_per_month / time_intervals.days_in_a_month / dca_amount_per_transaction
)
hours_to_pass_per_market_order: float = (
    time_intervals.hours_in_a_day / dca_transactions_per_day
)
