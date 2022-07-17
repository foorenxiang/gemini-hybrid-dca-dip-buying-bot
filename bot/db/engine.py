"""https://docs.sqlalchemy.org/en/14/orm/quickstart.html"""
from sqlalchemy import create_engine
from bot.config import database_connection_string

engine = create_engine(database_connection_string, echo=True, future=True)
