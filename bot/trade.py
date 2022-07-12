from typing import Tuple
import logging
from bot.models import GeminiOrder
from bot.heartbeat import handle_heartbeat
from bot.actions import (
    cancel_session_orders,
    make_tkn_market_order,
    make_tkn_limit_order,
)
from bot.heuristics import (
    is_to_make_dca_market_order,
    is_to_create_limit_orders,
    reset_limit_orders_if_insufficient_balance_for_dca,
)
from bot import config
import time

logger = logging.getLogger(__name__)


def handle_market_orders():
    try:
        if is_to_make_dca_market_order():
            new_market_order: GeminiOrder = make_tkn_market_order(
                tkn_pair="ethsgd",
                tkn_b_sell_qty=config.dca_amount_per_transaction,
            )
            print("Created market order")
            print(new_market_order)
    except Exception:
        logger.exception("Error while handling market orders")


def handle_limit_orders():
    try:
        reset_limit_orders_if_insufficient_balance_for_dca()
        limit_order_price_levels: Tuple[float] = is_to_create_limit_orders()
        if limit_order_price_levels:
            tkn_pair = "ETHSGD"
            for tkn_a_limit_price in limit_order_price_levels:
                tkn_b_sell_quantity: float = (
                    config.stop_limit_amount_per_stop_limit_order
                )
                new_limit_order: GeminiOrder = make_tkn_limit_order(
                    tkn_pair=tkn_pair,
                    tkn_b_sell_qty=tkn_b_sell_quantity,
                    tkn_a_buy_price=tkn_a_limit_price,
                )
                print("Created limit order")
                print(new_limit_order)
    except Exception:
        logger.exception("Error while handling limit orders")
        cancel_session_orders()


def slow_down_loop():
    time.sleep(config.trade_loop_delay_in_seconds)


def trade_loop():
    handle_heartbeat()
    handle_market_orders()
    if config.ENABLE_LIMIT_ORDERS:
        handle_limit_orders()
    slow_down_loop()


def trade():
    cancel_session_orders()
    while True:
        trade_loop()


def main():
    trade()


if __name__ == "__main__":
    main()
