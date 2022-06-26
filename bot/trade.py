from time import time
from typing import Optional, Tuple, Union
from pprint import pprint
from bot.models import GeminiOrder, GeminiTrade
from bot.heartbeat import handle_heartbeat
from bot.actions import get_my_trades, get_order_book, buy_tkn
from bot import config


# TODO finish up get all my orders first
def _get_open_limit_orders() -> Tuple[GeminiOrder]:
    def is_open_limit_order(order: GeminiOrder):
        return order.filled_time and order.limit_amount

    all_orders = (
        get_my_trades()
    )  # TODO refactor as get_my_trades only reflect completed trades, not open ones
    open_limit_orders = tuple(filter(is_open_limit_order, all_orders))
    return open_limit_orders


# TODO
def _is_filled_order(order: GeminiOrder):
    pass


def _get_filled_orders() -> Tuple[GeminiTrade]:
    filled_orders: Tuple[GeminiTrade] = get_my_trades()
    return filled_orders


# TODO
def _get_last_filled_order() -> GeminiTrade:
    last_filled_order: GeminiTrade = _get_filled_orders()[0]
    return GeminiTrade


def _get_current_time():
    current_epoch_time = time.time()
    return int(current_epoch_time)


def is_time_to_order(last_order: GeminiTrade) -> bool:
    last_order_time = last_order.timestamp
    current_time = _get_current_time()
    secs_in_hours = 3 * 3600
    return last_order_time - current_time > 3 * secs_in_hours


def is_price_low_enough(last_order: GeminiTrade, tkn_a_market_price: float) -> bool:
    percentage_delta: float = 1.2
    return last_order.price * percentage_delta >= tkn_a_market_price


def is_to_buy(last_order: GeminiTrade, tkn_a_market_price: float) -> bool:
    return all(
        [
            is_time_to_order(last_order),
            is_price_low_enough(last_order, tkn_a_market_price),
        ]
    )


# TODO
def trade_loop():
    print("my trades:")
    my_trades = get_my_trades()
    pprint(my_trades)
    last_order: GeminiTrade = _get_last_filled_order()
    tkn_a_market_price = get_order_book()
    if is_to_buy(last_order, tkn_a_market_price):

        new_gemini_order: GeminiOrder = buy_tkn(
            tkn_pair="ethsgd",
            tkn_b_sell_qty=config.dca_amount,
            tkn_a_buy_price=tkn_a_market_price,
        )
        print("Bought ")
    handle_heartbeat()


def trade(
    dca_amount: Optional[Union[int, float]] = None,
    max_tkn_b_market_price_in_tkn_a: Optional[Union[int, float]] = None,
):
    if isinstance(dca_amount, (int, float)) and dca_amount:
        config.dca_amount = dca_amount

    if (
        isinstance(max_tkn_b_market_price_in_tkn_a, (int, float))
        and max_tkn_b_market_price_in_tkn_a
    ):
        config.max_tkn_b_market_price_in_tkn_a = max_tkn_b_market_price_in_tkn_a

    while True:
        trade_loop()


if __name__ == "__main__":
    trade()
