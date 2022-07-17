from sqlalchemy import Boolean, Column, Float, String, BigInteger
from sqlalchemy.orm import declarative_base
from bot.db.engine import engine

Base = declarative_base()


class SQLTrade(Base):
    __tablename__ = "trades"
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    timestampms = Column(BigInteger, nullable=False)
    type = Column(String, nullable=False)
    aggressor = Column(Boolean, nullable=False)
    fee_currency = Column(String, nullable=False)
    fee_amount = Column(Float, nullable=False)
    tid = Column(BigInteger, primary_key=True, nullable=False)
    order_id = Column(BigInteger, nullable=False)
    exchange = Column(String, nullable=False)
    is_auction_fill = Column(Boolean, nullable=False)
    is_clearing_fill = Column(Boolean, nullable=False)
    symbol = Column(String, nullable=False)


Base.metadata.create_all(engine)
