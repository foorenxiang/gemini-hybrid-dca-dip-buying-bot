import time
from typing import Iterable, Tuple, Optional, Union
from bot.models import GeminiOrder, GeminiTrade, MarketPrices
from bot.actions import (
    get_tkn_b_account_balance,
    get_market_prices,
    get_my_trades,
    get_open_orders_by_decreasing_price,
    get_order_book,
    get_mean_trade_price,
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


def _is_price_low_enough(
    last_trade: GeminiTrade, tkn_a_market_prices: MarketPrices
) -> bool:
    return (
        last_trade.price
        * config.market_order_price_percentage_delta_to_last_trade_price
        >= tkn_a_market_prices.ask_price
    )


def _is_proposed_purchase_averaging_down(
    mean_trade_price: float, tkn_a_market_prices: MarketPrices
):
    return tkn_a_market_prices.ask_price < mean_trade_price


def _is_there_a_close_enough_open_order(
    highest_open_order: GeminiOrder,
    tkn_a_market_prices: MarketPrices,
):
    minimum_market_order_threshold = (
        highest_open_order.price
        * config.market_order_price_percentage_delta_to_highest_limit_order
    )
    return tkn_a_market_prices.ask_price > minimum_market_order_threshold


# TODO: finish this function
def _advanced_should_make_market_order_heuristic(trades: Tuple[GeminiTrade]) -> bool:
    print("Using advanced heuristic to determine if market order should be made")
    last_trade: Optional[GeminiTrade] = trades[0] if trades else None
    mean_trade_price = get_mean_trade_price(trades)
    open_orders_by_decreasing_price: Tuple[
        GeminiOrder
    ] = get_open_orders_by_decreasing_price()
    highest_open_order: Optional[GeminiOrder] = (
        open_orders_by_decreasing_price[0] if open_orders_by_decreasing_price else None
    )
    tkn_a_market_prices: MarketPrices = get_market_prices(tkn_pair="ethsgd")
    decision: bool = all(
        (
            _is_time_to_order(last_trade),
            _is_price_low_enough(last_trade, tkn_a_market_prices),
            _is_proposed_purchase_averaging_down(mean_trade_price, tkn_a_market_prices),
            _is_there_a_close_enough_open_order(
                open_orders_by_decreasing_price, tkn_a_market_prices
            ),
        )
    )
    return decision


def _simple_should_make_market_order_heuristic(trades: Tuple[GeminiTrade]) -> bool:
    print("Using simple heuristic to determine if market order should be made")
    last_trade: Optional[GeminiTrade] = trades[0] if trades else None
    decision: bool = _is_time_to_order(last_trade)
    return decision


def is_to_make_market_order() -> bool:
    trades = get_my_trades(symbol="ethsgd")
    return _simple_should_make_market_order_heuristic(trades)
    # return _advanced_should_make_market_order_heuristic(trades)


# TODO create function to get account balance as well. create limit orders based on existing limit orders, account balance,  market price and average purchase price
# TODO: refactor logic for when to buy
# TODO: finish this function
def _advanced_should_create_limit_orders_heuristic(
    trades: Tuple[GeminiTrade],
) -> Iterable[float]:
    tkn_b_account_balance = get_tkn_b_account_balance(token_b="sgd")
    mean_trade_price = get_mean_trade_price(trades)
    open_orders_by_decreasing_price: Tuple[
        GeminiOrder
    ] = get_open_orders_by_decreasing_price()
    tkn_a_market_price = get_order_book()
    last_trade = trades[0]
    result = None
    return result


def _compute_limit_order_decision(
    virtual_account_balance,
    current_stop_limit_price,
):
    minimum_limit_order_price = config.min_limit_order_price["ETHSGD"]
    minimum_balance_required_for_limit_orders = max(
        config.dca_amount_per_transaction,
        config.reserved_amount_for_market_orders["SGD"],
    )
    decision = all(
        (
            current_stop_limit_price > minimum_limit_order_price,
            virtual_account_balance > minimum_balance_required_for_limit_orders,
        )
    )
    return decision


def _simple_should_create_limit_orders_heuristic() -> Optional[Tuple[float]]:
    print("Using simple heuristic to determine if limit orders should be made")
    tkn_b_account_balance = get_tkn_b_account_balance(token_b="sgd")
    virtual_account_balance = tkn_b_account_balance
    maximum_limit_order_price = config.max_limit_order_price["ETHSGD"]
    minimum_limit_order_price = config.min_limit_order_price["ETHSGD"]
    open_orders_by_decreasing_price: Tuple[
        GeminiOrder
    ] = get_open_orders_by_decreasing_price()
    lowest_open_order: Optional[GeminiOrder] = (
        open_orders_by_decreasing_price[-1] if open_orders_by_decreasing_price else None
    )

    stop_limit_prices = []
    stop_limit_step = config.stop_limit_step["SGD"]
    current_ask_price = get_market_prices(tkn_pair="ethsgd").ask_price
    if lowest_open_order is None:
        current_stop_limit_price = current_ask_price - stop_limit_step
    else:
        current_stop_limit_price = (
            min(lowest_open_order.price, current_ask_price) - stop_limit_step
        )
    current_stop_limit_price = min(current_stop_limit_price, maximum_limit_order_price)

    if current_stop_limit_price < minimum_limit_order_price:
        return

    while _compute_limit_order_decision(
        virtual_account_balance,
        current_stop_limit_price,
    ):
        stop_limit_prices.append(current_stop_limit_price)
        current_stop_limit_price -= stop_limit_step
        virtual_account_balance = (
            tkn_b_account_balance - config.dca_amount_per_transaction
        )

    return tuple(stop_limit_prices)


def is_to_create_limit_orders() -> Optional[Tuple[float]]:
    # trades = get_my_trades(symbol="ethsgd")
    return _simple_should_create_limit_orders_heuristic()
    # return _advanced_should_create_limit_orders_heuristic(trades)
