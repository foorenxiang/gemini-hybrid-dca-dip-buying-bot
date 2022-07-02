"""https://docs.sqlalchemy.org/en/14/orm/quickstart.html"""
from sqlalchemy import create_engine, insert
from bot.db.models import Base, SQLTrade, SQLOrder
from bot.config import database_connection_string
from bot.models import GeminiOrder, GeminiTrade
from typing import Iterable

engine = create_engine(database_connection_string, echo=True, future=True)


# TODO: check why this process hangs
def _create_tables_in_db(engine):
    Base.metadata.create_all(engine)


def write_record_to_db(engine, model: Base):
    with engine.connect() as connection:
        connection.execute(model.__table__.insert(), model)


# TODO: finish this function
def all_read_trade_from_db() -> Iterable[GeminiOrder]:
    pass


# TODO: check if this is the correct way to write
def write_trade_to_db(trade: GeminiTrade):
    trade_record = SQLTrade(**trade.__dict__).save()
    write_record_to_db(trade_record)


# TODO: check if there's a more efficient way to bulk insert trades
def write_trades_to_db(trades: Iterable[GeminiTrade]):
    for trade in trades:
        write_trade_to_db(trade)


# TODO: finish up this function
def write_order_to_db(order: GeminiOrder):
    insert_statement = insert(SQLOrder).values(
        **order.__dict__
    )  # TODO: remember to check if datatypes have to be recasted between GeminiOrder and SQLOrder
    order_record = SQLOrder(**order.__dict__).save()
    write_record_to_db(order_record)


# TODO: check if there's a more efficient way to bulk insert orders
def write_orders_to_db(orders: Iterable[GeminiOrder]):
    for order in orders:
        write_order_to_db(order)


if __name__ == "__main__":
    _create_tables_in_db(engine)
