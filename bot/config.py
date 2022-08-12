from typing import Dict, NamedTuple, Union
from dotenv import dotenv_values
from pydantic import BaseModel
import pydantic
from bot.models import MarketPrices
from bot.utils import dotenv_path


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
    _env_values: _EnvironmentVariables = _EnvironmentVariables(
        **dotenv_values(dotenv_path)
    )
except pydantic.error_wrappers.ValidationError as e:
    raise ValueError(
        "Please create a .env file with the correct environment variables"
    ) from e
environment: str = _env_values.ENVIRONMENT
database: str = _env_values.SQL_DATABASE
database_connection_string: str = _env_values.SQL_DATABASE_CONNECTION_STRING

# Shared variables


class TimeIntervals(NamedTuple):
    hours_in_a_day: int = 24
    secs_in_a_min: int = 60
    seconds: int = 1


time_intervals = TimeIntervals()
client_order_id = "rx_trading_bot"
market_prices_cache: Dict[str, MarketPrices] = {}
trade_loop_delay_in_seconds = 5

# User config values
ENABLE_DCA_SELLING = False
monthly_reserved_amount_for_dca: float = 1500
dca_amount_per_transaction: float = 5.0  # in token_b_value
ENABLE_LIMIT_ORDERS: bool = True
tkn_pair_min_order_amount: Dict[str, float] = {
    "ETHSGD": 10**-3
}  # https://docs.gemini.com/rest-api/#basis-point
stop_limit_step: Dict[str, float] = {"SGD": 50, "ETH": 0.01, "BTC": 0.001}
limit_order_budget_per_month: float = 500  # in token_b_value # TODO: implement
limit_order_amount_per_transaction: Dict[
    str, Union[float, Dict[float, float]]
] = {  # in token_b_value
    "ETHSGD": {
        1: 50,
        1900: 25,
        6000: 10,
        10000: 5,
    },
    "BTCSGD": {},
}
limit_order_multiplier_for_stop_limit_step_adjustment_below_market_price = 4
max_tkn_b_market_price_in_tkn_a: float = 2000
market_order_price_percentage_delta_to_highest_limit_order: float = 1.05
market_order_price_percentage_delta_to_last_trade_price: float = 1.2
market_order_aggressiveness_factor: float = 1.3

backup_trades_to_db: bool = True


max_limit_order_price: Dict[str, float] = {
    tkn_pair: max(limit_order_amount_per_transaction[tkn_pair])
    for tkn_pair in limit_order_amount_per_transaction
    if limit_order_amount_per_transaction[tkn_pair]
}
min_limit_order_price: Dict[str, float] = {
    tkn_pair: min(limit_order_amount_per_transaction[tkn_pair])
    for tkn_pair in limit_order_amount_per_transaction
    if limit_order_amount_per_transaction[tkn_pair]
}
