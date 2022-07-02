from typing import Optional, Tuple, Union
from pprint import pprint
from bot.models import GeminiOrder
from bot.heartbeat import handle_heartbeat
from bot.actions import (
    make_tkn_market_order,
    make_tkn_limit_order,
)
from bot.heuristics import is_to_make_market_order, is_to_create_limit_orders
from bot import config


def trade_loop():
    handle_heartbeat()
    orders_created_in_loop = []
    if is_to_make_market_order():
        new_gemini_order: GeminiOrder = make_tkn_market_order(
            tkn_pair="ethsgd",
            tkn_b_sell_qty=config.dca_amount,
        )
        orders_created_in_loop.append(new_gemini_order)

    limit_order_price_levels: Tuple[float] = is_to_create_limit_orders()
    if limit_order_price_levels:
        for tkn_a_limit_price in limit_order_price_levels:
            limit_order: GeminiOrder = make_tkn_limit_order(
                tkn_pair="ethsgd",
                tkn_b_sell_qty=config.dca_amount,
                tkn_a_buy_price=tkn_a_limit_price,
            )
            orders_created_in_loop.append(limit_order)
    print("New gemini orders created in loop:")
    pprint(orders_created_in_loop)


def trade(
    dca_amount: Optional[Union[int, float]] = None,
    max_tkn_b_market_price_in_tkn_a: Optional[Union[int, float]] = None,
):
    if isinstance(dca_amount, (int, float)) and dca_amount:
        config.dca_amount = dca_amount

    if max_tkn_b_market_price_in_tkn_a and isinstance(
        max_tkn_b_market_price_in_tkn_a, (int, float)
    ):
        config.max_tkn_b_market_price_in_tkn_a = max_tkn_b_market_price_in_tkn_a
    while True:
        trade_loop()


def main():
    trade()


if __name__ == "__main__":
    main()
