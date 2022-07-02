from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple
from bot.models import (
    GeminiOrder,
    GeminiTrade,
    MarketPrices,
    OrderActions,
    GeminiBalance,
)
from bot.rest_api_handler import (
    compute_payload_nonce,
    request_private_endpoint,
    request_public_endpoint,
    cast_response_to_gemini_order,
)
from bot import config


def _cast_to_gemini_balance(balance_record: dict) -> GeminiBalance:
    return GeminiBalance(
        type=balance_record["type"],
        currency=balance_record["currency"],
        amount=float(balance_record["amount"]),
        available=float(balance_record["available"]),
        availableForWithdrawal=float(balance_record["availableForWithdrawal"]),
    )


def get_available_balances() -> Dict[str, GeminiBalance]:
    endpoint = "/v1/balances"
    payload = {"request": endpoint, "nonce": compute_payload_nonce()}
    balances_data: List[dict] = request_private_endpoint(endpoint, payload)
    available_balances_iterable: Iterable[GeminiBalance] = (
        _cast_to_gemini_balance(balance_record) for balance_record in balances_data
    )
    available_balances: Dict[str, GeminiBalance] = {
        balance.currency: balance for balance in available_balances_iterable
    }
    return available_balances


def get_tkn_b_account_balance(token_b="sgd") -> float:
    available_balance = get_available_balances()[token_b.upper()].available
    return available_balance


def _cast_to_gemini_order(open_order_record: dict):
    return GeminiOrder(
        avg_execution_price=float(open_order_record["avg_execution_price"]),
        executed_amount=float(open_order_record["executed_amount"]),
        options=open_order_record["options"],
        order_id=int(open_order_record["order_id"]),
        original_amount=float(open_order_record["original_amount"]),
        price=float(open_order_record["price"]),
        remaining_amount=float(open_order_record["remaining_amount"]),
        side=open_order_record["side"],
        symbol=open_order_record["symbol"],
        timestamp=int(open_order_record["timestamp"]),
        type=open_order_record["type"],
    )


def get_open_orders_by_decreasing_price() -> Tuple[GeminiOrder]:
    open_orders = get_open_orders()
    open_orders_in_decreasing_price = sorted(
        open_orders, key=lambda order: order.price, reverse=True
    )
    return open_orders_in_decreasing_price


def get_open_orders() -> Tuple[GeminiOrder]:
    endpoint = "/v1/orders"
    payload = {"request": endpoint, "nonce": compute_payload_nonce()}
    open_order_records: List[dict] = request_private_endpoint(endpoint, payload)
    open_orders = tuple(
        _cast_to_gemini_order(open_order_record)
        for open_order_record in open_order_records
    )
    return open_orders


def _cast_to_gemini_trade(trade_record: dict) -> GeminiTrade:
    return GeminiTrade(
        price=float(trade_record["price"]),
        amount=float(trade_record["amount"]),
        timestamp=int(trade_record["timestamp"]),
        timestampms=int(trade_record["timestampms"]),
        type=OrderActions.BUY if trade_record["type"] == "Buy" else OrderActions.SELL,
        aggressor=trade_record["aggressor"] == "true",
        fee_currency=trade_record["fee_currency"],
        fee_amount=float(trade_record["fee_amount"]),
        tid=int(trade_record["tid"]),
        order_id=int(trade_record["order_id"]),
        exchange=trade_record["exchange"],
        is_auction_fill=trade_record["is_auction_fill"] == "true",
        is_clearing_fill=trade_record["is_clearing_fill"] == "true",
        symbol=str(trade_record["symbol"]),
    )


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

    trade_records: List[dict] = request_private_endpoint(endpoint, payload)
    trades = (_cast_to_gemini_trade(trade_record) for trade_record in trade_records)
    trades_in_reverse_chronological_order = tuple(
        sorted(trades, key=lambda order: order.timestampms, reverse=True)
    )
    return trades_in_reverse_chronological_order


def make_tkn_market_order(
    tkn_pair: str,
    tkn_b_sell_qty: float,
) -> Optional[GeminiOrder]:
    """
    The API doesn't directly support market orders because they provide you with no price protection.

    Instead, use the “immediate-or-cancel” order execution option, coupled with an aggressive limit price (i.e. very high for a buy order or very low for a sell order), to achieve the same result.
    """
    tkn_a_market_price = get_market_prices(tkn_pair).ask_price
    aggressive_limit_price = (
        tkn_a_market_price * config.market_order_aggressiveness_factor
    )
    return make_tkn_limit_order(
        tkn_pair=tkn_pair,
        tkn_b_sell_qty=tkn_b_sell_qty * config.market_order_aggressiveness_factor,
        tkn_a_buy_price=aggressive_limit_price,
    )


def make_tkn_limit_order(
    tkn_pair: str,
    tkn_b_sell_qty: float,
    tkn_a_buy_price: float,
) -> Optional[GeminiOrder]:
    endpoint = "/v1/order/new"
    nonce = compute_payload_nonce()
    client_order_id = f"{config.client_order_id}_{nonce}"
    order_amount = tkn_b_sell_qty / tkn_a_buy_price
    payload = {
        "request": endpoint,
        "nonce": nonce,
        "client_order_id": client_order_id,
        "symbol": tkn_pair,
        "amount": f"{order_amount:.5f}",
        "price": f"{tkn_a_buy_price:.2f}",
        "side": "buy",
        "type": "exchange limit",
    }
    response = request_private_endpoint(endpoint, payload)
    return cast_response_to_gemini_order(response)


def get_order_book(tkn_pair: str = "ethsgd"):
    return request_public_endpoint(
        f"/v1/book/{tkn_pair}",
        url_parameters={
            "limit_bids": 1,
            "limit_asks": 1,
        },
    )


def get_market_prices(tkn_pair: str = "ethsgd") -> MarketPrices:
    order_book = get_order_book(tkn_pair)
    return MarketPrices(
        tkn_pair=tkn_pair,
        ask_price=float(order_book["asks"][0]["price"]),
        bid_price=float(order_book["bids"][0]["price"]),
    )


def _print_trade_data(
    number_of_trades: int,
    trade: GeminiTrade,
):
    trade_date = datetime.fromtimestamp(trade.timestamp)
    print(f"Trade {number_of_trades + 1} for {trade.symbol}")
    print(trade.type.value, trade_date, trade.price, trade.amount)


@dataclass
class TokenPairMeanTradeStore:
    tkn_pair: str
    tkn_a_bought: float = 0
    tkn_b_spent: float = 0
    number_of_trades: int = 0
    average_price: float = 0


def _add_new_token_pair_to_store(
    token_pair_stores: Dict[str, TokenPairMeanTradeStore], trade: GeminiTrade
):
    token_pair_stores[trade.symbol] = TokenPairMeanTradeStore(tkn_pair=trade.symbol)


def _process_buy_transaction(
    trade: GeminiTrade, token_pair_store: TokenPairMeanTradeStore
):
    token_pair_store.tkn_a_bought += trade.amount
    token_pair_store.tkn_b_spent += trade.price * trade.amount
    token_pair_store.tkn_b_spent += trade.fee_amount


def _process_sell_transaction(
    trade: GeminiTrade, token_pair_store: TokenPairMeanTradeStore
):
    token_pair_store.tkn_a_bought -= trade.amount
    token_pair_store.tkn_b_spent -= trade.price * trade.amount
    token_pair_store.tkn_b_spent += trade.fee_amount


def _add_token_pair_trade_data_to_store(
    trade: GeminiTrade,
    token_pair_store: TokenPairMeanTradeStore,
    verbose: bool,
):
    token_pair_store.number_of_trades += 1
    if trade.type == OrderActions.BUY:
        _process_buy_transaction(trade, token_pair_store)
    elif trade.type == OrderActions.SELL:
        _process_sell_transaction(trade, token_pair_store)
    else:
        raise ValueError(f"Unknown trade type: {trade.type}")
    if verbose:
        _print_trade_data(token_pair_store.number_of_trades, trade)


def _retrieve_token_pair_store(
    token_pair_stores: Dict[str, TokenPairMeanTradeStore], trade: GeminiTrade
):
    token_pair_store = token_pair_stores[trade.symbol]
    return token_pair_store


def _aggregate_mean_of_token_pair_store(token_pair_store: TokenPairMeanTradeStore):
    token_pair_store.average_price = (
        token_pair_store.tkn_b_spent / token_pair_store.tkn_a_bought
    )
    print(
        f"For {token_pair_store.tkn_pair}: bought a net total of {token_pair_store.tkn_a_bought} for {token_pair_store.tkn_b_spent} for an average of {token_pair_store.average_price} over {token_pair_store.number_of_trades} trades"
    )


def _aggregate_means_of_token_pair_stores(token_pair_stores: TokenPairMeanTradeStore):
    for token_pair_store in token_pair_stores.values():
        _aggregate_mean_of_token_pair_store(token_pair_store)
    return token_pair_store


def _ingest_trades_to_mean_trade_data_store(
    trades: Tuple[GeminiTrade],
    token_pair_stores: Dict[str, TokenPairMeanTradeStore],
    verbose: bool,
):
    for trade in trades:
        if trade.symbol not in token_pair_stores:
            _add_new_token_pair_to_store(token_pair_stores, trade)
        token_pair_store = _retrieve_token_pair_store(token_pair_stores, trade)
        _add_token_pair_trade_data_to_store(trade, token_pair_store, verbose)


def get_mean_trade_prices(
    trades: Tuple[GeminiTrade],
    verbose=True,
) -> Dict[str, TokenPairMeanTradeStore]:
    if not trades:
        return

    token_pair_stores: Dict[str, TokenPairMeanTradeStore] = {}
    _ingest_trades_to_mean_trade_data_store(trades, token_pair_stores, verbose)
    _aggregate_means_of_token_pair_stores(token_pair_stores)
    return token_pair_stores


def get_mean_trade_price(
    trades: Tuple[GeminiTrade],
    token_pair: str = "ethsgd",
    verbose=True,
) -> Optional[Tuple[float, int, float, float]]:
    token_pair_stores = get_mean_trade_prices(trades, verbose)
    token_pair_store: TokenPairMeanTradeStore = token_pair_stores[token_pair.upper()]
    return (
        token_pair_store.average_price,
        token_pair_store.number_of_trades,
        token_pair_store.tkn_a_bought,
        token_pair_store.tkn_b_spent,
    )


if __name__ == "__main__":
    from pprint import pprint

    print("Get all my trades")
    my_trades = get_my_trades(symbol="ethsgd")
    print(f"{len(my_trades)} trades found")
    pprint(my_trades)
    print("Open orders:")
    my_open_orders = get_open_orders()
    print(f"{len(my_open_orders)} open orders found")
    pprint(my_open_orders)
    print(get_mean_trade_price(my_trades))
    print("Order book")
    print(get_market_prices())
    print("Available balances")
    pprint(get_available_balances())
    print("SGD Balance")
    pprint(get_tkn_b_account_balance(token_b="sgd"))
