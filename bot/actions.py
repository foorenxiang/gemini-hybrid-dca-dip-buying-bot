from datetime import datetime
from pprint import pprint
from typing import Optional, Tuple
from bot.models import GeminiOrder, GeminiTrade, OrderActions
from bot.rest_api_handler import (
    compute_payload_nonce,
    request_private_endpoint,
    request_public_endpoint,
    cast_response_to_gemini_order,
)


def get_open_orders() -> Tuple[GeminiOrder]:
    endpoint = "/v1/orders"
    payload = {"request": endpoint, "nonce": compute_payload_nonce()}
    open_orders = (
        GeminiOrder(
            avg_execution_price=float(open_order["avg_execution_price"]),
            executed_amount=float(open_order["executed_amount"]),
            options=open_order["options"],
            order_id=int(open_order["order_id"]),
            original_amount=float(open_order["original_amount"]),
            price=float(open_order["price"]),
            remaining_amount=float(open_order["remaining_amount"]),
            side=open_order["side"],
            symbol=open_order["symbol"],
            timestamp=int(open_order["timestamp"]),
            type=open_order["type"],
        )
        for open_order in request_private_endpoint(endpoint, payload)
    )
    orders_in_reverse_chronological_order = sorted(
        open_orders, key=lambda order: order.timestamp, reverse=True
    )
    return orders_in_reverse_chronological_order


def get_my_trades(limit_trades: int = 500, symbol="ethsgd") -> Tuple[GeminiTrade]:
    endpoint = "/v1/mytrades"
    payload = {
        "request": endpoint,
        "nonce": compute_payload_nonce(),
    }

    if symbol:
        payload["symbol"] = symbol

    if isinstance(limit_trades, (float, int)):
        if limit_trades > 500:
            limit_trades = 500
        elif limit_trades < 50:
            limit_trades = 50
        payload["limit_trades"] = limit_trades

    trades = (
        GeminiTrade(
            price=float(trades["price"]),
            amount=float(trades["amount"]),
            timestamp=int(trades["timestamp"]),
            timestampms=int(trades["timestampms"]),
            type=OrderActions.BUY if trades["type"] == "Buy" else OrderActions.SELL,
            aggressor=trades["aggressor"] == "true",
            fee_currency=trades["fee_currency"],
            fee_amount=float(trades["fee_amount"]),
            tid=int(trades["tid"]),
            order_id=int(trades["order_id"]),
            exchange=trades["exchange"],
            is_auction_fill=trades["is_auction_fill"] == "true",
            is_clearing_fill=trades["is_clearing_fill"] == "true",
            symbol=str(trades["symbol"]),
        )
        for trades in request_private_endpoint(endpoint, payload)
    )
    trades_in_reverse_chronological_order = tuple(
        sorted(trades, key=lambda order: order.timestampms, reverse=True)
    )
    return trades_in_reverse_chronological_order


def buy_tkn(
    tkn_pair: str, tkn_b_sell_qty: float, tkn_a_buy_price: float
) -> Optional[GeminiOrder]:
    endpoint = "/v1/order/new"
    payload = {
        "request": endpoint,
        "nonce": compute_payload_nonce(),
        "symbol": tkn_pair,
        "amount": str(tkn_b_sell_qty / tkn_a_buy_price),
        "price": str(tkn_a_buy_price),
        "side": "buy",
        "type": "exchange limit",
        "options": ["maker-or-cancel"],
    }
    response = request_private_endpoint(endpoint, payload)
    return cast_response_to_gemini_order(response)


def get_order_book():
    return request_public_endpoint(
        "/v1/book/ethsgd",
        url_parameters={
            "limit_bids": 1,
            "limit_asks": 1,
        },
    )


def _print_trade_data(number_of_trades: int, idx: int, trade: GeminiTrade):
    trade_date = datetime.fromtimestamp(trade.timestamp)
    print("trade", idx, "of", number_of_trades)
    print(trade.type.value, trade_date, trade.price, trade.amount)


def mean_buy_price(
    tkn_pair: str = "ethsgd", verbose=True
) -> Tuple[float, int, float, float]:
    print("##############")
    trades: Tuple[GeminiTrade] = get_my_trades(limit_trades=500, symbol=tkn_pair)
    tkn_a_bought: float = 0
    tkn_b_spent: float = 0
    number_of_trades = len(trades)
    print("Number of trades:", number_of_trades)
    for idx, trade in enumerate(trades):
        assert trade.symbol.lower() == tkn_pair.lower()
        if trade.type == OrderActions.BUY:
            tkn_a_bought += trade.amount
            tkn_b_spent += trade.price * trade.amount
            tkn_b_spent += trade.fee_amount
        elif trade.type == OrderActions.SELL:
            tkn_a_bought -= trade.amount
            tkn_b_spent -= trade.price * trade.amount
            tkn_b_spent += trade.fee_amount
        else:
            raise ValueError(f"Unknown trade type: {trade.type}")
        if verbose:
            _print_trade_data(number_of_trades, idx, trade)

    average_price = tkn_b_spent / tkn_a_bought
    print(
        f"For {tkn_pair}: {tkn_a_bought} bought, {tkn_b_spent} spent for an average of {average_price}"
    )
    return (
        average_price,
        number_of_trades,
        tkn_a_bought,
        tkn_b_spent,
    )


if __name__ == "__main__":
    print("Get all my trades")
    my_trades = get_my_trades()
    print(f"{len(my_trades)} trades found")
    pprint(my_trades)
    print("Open orders:")
    my_open_orders = get_open_orders()
    print(f"{len(my_open_orders)} open orders found")
    pprint(my_open_orders)
    mean_buy_price()
