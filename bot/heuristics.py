import time
from typing import Iterable, List, Tuple, Optional, Union
from bot.models import GeminiOrder, GeminiTrade, OrderActions
from bot.actions import (
    cancel_session_orders,
    get_tkn_b_account_balance,
    get_market_prices,
    get_my_trades,
    get_open_orders_by_decreasing_price,
)
from bot.utils import get_day_of_month_and_days_in_month
from bot import config


def _get_current_time():
    current_epoch_time = time.time()
    return int(current_epoch_time)


def hours_to_pass_per_market_order() -> float:
    days_in_current_month = get_day_of_month_and_days_in_month()[1]
    dca_transactions_per_day = (
        config.monthly_reserved_amount_for_dca
        / days_in_current_month
        / config.dca_amount_per_transaction
    )
    return config.time_intervals.hours_in_a_day / dca_transactions_per_day


def _is_time_to_order(last_trade: Union[GeminiTrade, None]) -> bool:
    if last_trade is None:
        return True
    last_order_time = last_trade.timestamp
    current_time = _get_current_time()
    MINIMUM_SECONDS_TO_PASS_BEFORE_MAKING_MARKET_ORDER: int = int(
        3600 * hours_to_pass_per_market_order()
    )
    return (
        current_time
        > last_order_time + MINIMUM_SECONDS_TO_PASS_BEFORE_MAKING_MARKET_ORDER
    )


def reset_limit_orders_if_insufficient_balance_for_dca():
    remaining_dca_budget = calculate_remaining_dca_budget_for_month()
    tkn_b_account_balance: float = get_tkn_b_account_balance(token_b="sgd")
    if tkn_b_account_balance < remaining_dca_budget:
        cancel_session_orders()
        print("Reset limit orders as current balance is insufficient for dca")


def is_to_make_market_order() -> bool:
    all_trades: Tuple[GeminiTrade] = get_my_trades(symbol="ethsgd")
    purchase_trades = [trade for trade in all_trades if trade.type == OrderActions.BUY]
    print("Determining if DCA market order should be made")
    last_trade: Optional[GeminiTrade] = purchase_trades[0] if purchase_trades else None
    decision: bool = _is_time_to_order(last_trade)
    return decision


def calculate_remaining_dca_budget_for_month() -> float:
    (
        day_of_month,
        days_in_current_month,
    ) = get_day_of_month_and_days_in_month()
    remaining_dca_budget_for_calendar_month = (
        config.monthly_reserved_amount_for_dca
        / days_in_current_month
        * (days_in_current_month - day_of_month + 1)
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


def get_stop_limit_prices_to_consider(
    maximum_limit_order_price: float,
    minimum_limit_order_price: float,
    stop_limit_step: float,
    current_ask_price: float,
) -> Tuple[List[float], List[float]]:
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
    return stop_limit_prices_to_consider, proposed_new_stop_limit_prices


def get_existing_limit_prices_intervals(stop_limit_prices_to_consider: List[float]):
    existing_limit_price_intervals: Iterable[Tuple[float, float]] = zip(
        stop_limit_prices_to_consider,
        stop_limit_prices_to_consider[1:],
    )
    return existing_limit_price_intervals


def is_to_create_limit_orders() -> Optional[Tuple[float]]:
    print("Determining if limit orders should be made")
    tkn_b_account_balance: float = get_tkn_b_account_balance(token_b="sgd")
    maximum_limit_order_price: float = config.max_limit_order_price["ETHSGD"]
    minimum_limit_order_price: float = config.min_limit_order_price["ETHSGD"]
    stop_limit_step: float = config.stop_limit_step["SGD"]
    current_ask_price: float = get_market_prices(tkn_pair="ethsgd").ask_price

    (
        stop_limit_prices_to_consider,
        proposed_new_stop_limit_prices,
    ) = get_stop_limit_prices_to_consider(
        maximum_limit_order_price,
        minimum_limit_order_price,
        stop_limit_step,
        current_ask_price,
    )

    existing_limit_price_intervals = get_existing_limit_prices_intervals(
        stop_limit_prices_to_consider
    )

    new_stop_limit_prices = compute_stop_limit_prices(
        tkn_b_account_balance,
        stop_limit_step,
        proposed_new_stop_limit_prices,
        existing_limit_price_intervals,
    )
    return new_stop_limit_prices


def compute_stop_limit_prices(
    tkn_b_account_balance: float,
    stop_limit_step: float,
    proposed_new_stop_limit_prices: List[float],
    existing_limit_price_intervals: Iterable[Tuple[float, float]],
):
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
    new_stop_limit_prices = tuple(
        sorted(proposed_new_stop_limit_prices, reverse=True)[
            :number_of_limits_order_to_create
        ]
    )

    return new_stop_limit_prices
