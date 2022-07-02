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
    return current_time > last_order_time + config.minimum_seconds_before_market_orders


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


def _simple_should_create_limit_orders_heuristic() -> Iterable[float]:
    tkn_b_account_balance = get_tkn_b_account_balance(token_b="sgd")
    open_orders_by_decreasing_price: Tuple[
        GeminiOrder
    ] = get_open_orders_by_decreasing_price()
    lowest_open_order: Optional[GeminiOrder] = (
        open_orders_by_decreasing_price[-1] if open_orders_by_decreasing_price else None
    )
    decision = (
        tkn_b_account_balance > config.dca_amount
        and config.automatic_stop_limit_price_steps_for_buying_dip > config.dca_amount
        and lowest_open_order is not None
        and lowest_open_order.price > config.dca_amount
    )

    if decision:
        stop_limit_steps = []
        stop_limit_step = lowest_open_order.price - config.dca_amount
        adjusted_account_balance = tkn_b_account_balance - config.dca_amount
        while True:
            stop_limit_step -= config.dca_amount
            adjusted_account_balance -= config.dca_amount
            if (
                stop_limit_step < config.dca_amount
                or adjusted_account_balance < config.dca_amount
            ):
                break
            stop_limit_steps.append(stop_limit_step)
        return tuple(stop_limit_steps)
    return tuple()


def is_to_create_limit_orders() -> Tuple[float]:
    # trades = get_my_trades(symbol="ethsgd")
    return _simple_should_create_limit_orders_heuristic()
    # return _advanced_should_create_limit_orders_heuristic(trades)
