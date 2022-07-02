from dotenv import dotenv_values
from pydantic import BaseModel


class _EnvironmentVariables(BaseModel):
    ENVIRONMENT: str
    GEMINI_TRADING_API_KEY: str
    GEMINI_TRADING_API_SECRET: str
    SQL_DATABASE_CONNECTION_STRING: str
    SQL_DATABASE: str
    SQL_USERNAME: str
    SQL_PASSWORD: str


_env_values: _EnvironmentVariables = _EnvironmentVariables(**dotenv_values())
environment: str = _env_values.ENVIRONMENT
database: str = _env_values.SQL_DATABASE
database_connection_string: str = _env_values.SQL_DATABASE_CONNECTION_STRING

dca_amount: float = 3.0  # in token_b_value
# minimum_seconds_before_market_orders: int = 3600 * 3
minimum_seconds_before_market_orders: int = 1
max_tkn_b_market_price_in_tkn_a: float = 2000
market_order_price_percentage_delta_to_highest_limit_order: float = 1.05
market_order_price_percentage_delta_to_last_trade_price: float = 1.2
market_order_aggressiveness_factor: float = 1.3
automatic_stop_limit_price_steps_for_buying_dip = 50  # in token_b_value

client_order_id = "rx_trading_bot"
