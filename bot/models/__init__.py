from typing import List
from enum import Enum
from pydantic import BaseModel


class OrderActions(Enum):
    BUY = "BUY"
    SELL = "SELL"


class GeminiOrder(BaseModel):
    """An open order"""

    avg_execution_price: float  # '0.00',
    executed_amount: float  # '0',
    options: List[str]  # ['maker-or-cancel'],
    order_id: int  # '1857290169',
    original_amount: float  # '5',
    price: float  # '100.00',
    remaining_amount: float  # '5',
    side: str  # 'buy',
    symbol: str  # 'ethsgd',
    timestamp: int  # '1656252803',
    type: str  # 'exchange limit',
    # was_forced: bool  # False
    # timestampms: int  # 1656252803361,
    # is_hidden: bool  # False,
    # id: int  # '1857290169',
    # exchange : str # 'gemini',
    # is_cancelled : bool # False,
    # is_live : bool # True,


class GeminiTrade(BaseModel):
    """An order which has at least partial filling"""

    price: float
    amount: float
    timestamp: int
    timestampms: int
    type: OrderActions
    aggressor: bool
    fee_currency: str
    fee_amount: float
    tid: int
    order_id: int
    exchange: str
    is_auction_fill: bool
    is_clearing_fill: bool
    symbol: str
