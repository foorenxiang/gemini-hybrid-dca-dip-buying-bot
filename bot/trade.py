from typing import Tuple
from bot.models import GeminiOrder
from bot.heartbeat import handle_heartbeat
from bot.actions import (
    make_tkn_market_order,
    make_tkn_limit_order,
)
from bot.heuristics import is_to_make_market_order, is_to_create_limit_orders
from bot import config


def handle_market_orders():
    if is_to_make_market_order():
        new_market_order: GeminiOrder = make_tkn_market_order(
            tkn_pair="ethsgd",
            tkn_b_sell_qty=config.dca_amount_per_transaction,
        )
        print("Created market order")
        print(new_market_order)


def handle_limit_orders():
    limit_order_price_levels: Tuple[float] = is_to_create_limit_orders()
    if limit_order_price_levels:
        for tkn_a_limit_price in limit_order_price_levels:
            new_limit_order: GeminiOrder = make_tkn_limit_order(
                tkn_pair="ethsgd",
                tkn_b_sell_qty=config.limit_order_amount_per_transaction,
                tkn_a_buy_price=tkn_a_limit_price,
            )
            print("Created limit order")
            print(new_limit_order)


def trade_loop():
    handle_heartbeat()
    handle_market_orders()
    handle_limit_orders()


def trade():
    while True:
        trade_loop()


def main():
    trade()


if __name__ == "__main__":
    main()
