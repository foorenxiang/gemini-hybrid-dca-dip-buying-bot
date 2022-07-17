"""https://docs.sqlalchemy.org/en/14/orm/quickstart.html"""
import traceback
from typing import Iterable
from bot.db.session import session
from bot.db.models import SQLTrade
from bot.models import GeminiTrade, OrderActions


def retrieve_stored_trades() -> Iterable[GeminiTrade]:
    trades: Iterable[GeminiTrade] = (
        cast_SQLTrade_to_GeminiTrade(trade) for trade in session.query(SQLTrade).all()
    )
    return trades


def cast_SQLTrade_to_GeminiTrade(trade: SQLTrade) -> GeminiTrade:
    trade_dict = trade.__dict__.copy()
    trade_dict["type"] = getattr(OrderActions, trade_dict["type"].upper())
    trade = GeminiTrade(**trade_dict)
    return trade


def cast_GeminiTrade_to_SQLTrade(trade: GeminiTrade) -> SQLTrade:
    trade_data = trade.__dict__.copy()
    trade_data["type"]: OrderActions
    trade_data["type"] = trade_data["type"].value
    trade_record = SQLTrade(**trade_data)
    return trade_record


def write_trade_to_db(trade: GeminiTrade):
    try:
        session.add(cast_GeminiTrade_to_SQLTrade(trade))
        session.commit()
    except Exception:
        print("Encountered error while writing trade to db")
        print(trade)
        traceback.print_exc()


def write_trades_to_db(trades: Iterable[GeminiTrade]):
    for trade in trades:
        write_trade_to_db(trade)
