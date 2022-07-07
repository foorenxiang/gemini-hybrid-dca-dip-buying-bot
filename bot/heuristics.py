import time
import calendar
from datetime import datetime
from typing import Iterable, List, Tuple, Optional, Union
from bot.models import GeminiOrder, GeminiTrade, OrderActions
from bot.actions import (
    get_tkn_b_account_balance,
    get_market_prices,
    get_my_trades,
    get_open_orders_by_decreasing_price,
)
from bot import config


def _get_current_time():
    current_epoch_time = time.time()
    return int(current_epoch_time)


def _is_time_to_order(last_trade: Union[GeminiTrade, None]) -> bool:
    if last_trade is None:
        return True
    last_order_time = last_trade.timestamp
    current_time = _get_current_time()
    MINIMUM_SECONDS_TO_PASS_BEFORE_MAKING_MARKET_ORDER: int = int(
        3600 * config.hours_to_pass_per_market_order
    )
    return (
        current_time
        > last_order_time + MINIMUM_SECONDS_TO_PASS_BEFORE_MAKING_MARKET_ORDER
    )


def is_to_make_market_order() -> bool:
    all_trades: Tuple[GeminiTrade] = get_my_trades(symbol="ethsgd")
    purchase_trades = [trade for trade in all_trades if trade.type == OrderActions.BUY]
    print("Determining if DCA market order should be made")
    last_trade: Optional[GeminiTrade] = purchase_trades[0] if purchase_trades else None
    decision: bool = _is_time_to_order(last_trade)
    return decision


def calculate_remaining_dca_budget_for_month() -> float:
    now = datetime.now()
    day_of_month: int = now.day
    days_in_current_month = calendar.monthrange(now.year, now.month)[1]
    remaining_dca_budget_for_calendar_month = (
        config.monthly_reserved_amount_for_market_orders["SGD"]
        / (days_in_current_month - day_of_month + 1)
        * days_in_current_month
    )
    print(
        "Remaining reserved dca budget for calendar month:",
        remaining_dca_budget_for_calendar_month,
    )
    return remaining_dca_budget_for_calendar_month


def calculate_available_balance_for_limit_orders(tkn_b_account_balance: float) -> float:
    available_balance_for_limit_orders = (
        tkn_b_account_balance - calculate_remaining_dca_budget_for_month()
    )
    return available_balance_for_limit_orders


def is_to_create_limit_orders() -> Optional[Tuple[float]]:
    print("Determining if limit orders should be made")
    tkn_b_account_balance: float = get_tkn_b_account_balance(token_b="sgd")
    maximum_limit_order_price: float = config.max_limit_order_price["ETHSGD"]
    minimum_limit_order_price: float = config.min_limit_order_price["ETHSGD"]
    stop_limit_step: float = config.stop_limit_step["SGD"]
    current_ask_price: float = get_market_prices(tkn_pair="ethsgd").ask_price
    open_orders_by_decreasing_price: Tuple[
        GeminiOrder
    ] = get_open_orders_by_decreasing_price()
    open_purchase_orders_by_decreasing_price = (
        order for order in open_orders_by_decreasing_price if order.side == "buy"
    )
    existing_stop_limit_prices_in_ascending_order = sorted(
        order.price for order in open_purchase_orders_by_decreasing_price
    )
    stop_limit_prices_to_consider = [*existing_stop_limit_prices_in_ascending_order]
    proposed_new_stop_limit_prices: List[float] = []

    maximum_limit_order_price_for_loop = min(
        maximum_limit_order_price,
        current_ask_price
        - (
            config.limit_order_multiplier_for_stop_limit_step_adjustment_below_market_price
            * stop_limit_step
        ),
    )

    if (
        max(stop_limit_prices_to_consider, default=0) + stop_limit_step
        <= maximum_limit_order_price_for_loop
    ):
        proposed_new_stop_limit_prices.append(maximum_limit_order_price_for_loop)
        stop_limit_prices_to_consider.append(maximum_limit_order_price_for_loop)

    if (
        min(stop_limit_prices_to_consider, default=float("inf")) - stop_limit_step
        >= minimum_limit_order_price
    ):
        proposed_new_stop_limit_prices.append(minimum_limit_order_price)
        stop_limit_prices_to_consider.append(minimum_limit_order_price)

    stop_limit_prices_to_consider.sort()

    existing_limit_price_intervals: Iterable[Tuple[float, float]] = zip(
        stop_limit_prices_to_consider,
        stop_limit_prices_to_consider[1:],
    )

    for price_interval in existing_limit_price_intervals:
        lower_price, higher_price = price_interval
        price_delta = higher_price - lower_price
        limit_price = lower_price
        while price_delta > stop_limit_step:
            limit_price += stop_limit_step
            price_delta -= stop_limit_step
            if limit_price + stop_limit_step > higher_price:
                break
            proposed_new_stop_limit_prices.append(limit_price)

    available_balance_for_limit_orders = calculate_available_balance_for_limit_orders(
        tkn_b_account_balance
    )
    number_of_limits_order_to_create = int(
        available_balance_for_limit_orders
        / config.stop_limit_amount_per_stop_limit_order
    )
    new_stop_limit_prices = sorted(proposed_new_stop_limit_prices, reverse=True)[
        :number_of_limits_order_to_create
    ]
    return tuple(new_stop_limit_prices)
