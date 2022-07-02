from sqlalchemy import Boolean, Column, Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SQLTrade(Base):
    __tablename__ = "trades"
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)
    timestammpms = Column(Integer, nullable=False)
    order_action = Column(String, nullable=False)
    aggressor = Column(Boolean, nullable=False)
    fee_currency = Column(String, nullable=False)
    fee_amount = Column(Float, nullable=False)
    tid = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    exchange = Column(String, nullable=False)
    is_auction_fill = Column(Boolean, nullable=False)
    is_clearing = Column(Boolean, nullable=False)
    symbol = Column(String, nullable=False)


class SQLOrder(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True)
    avg_execution_price = Column(Float, nullable=False)
    executed_amount = Column(Float, nullable=False)
    options = Column(String, nullable=False)
    original_amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    side = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
