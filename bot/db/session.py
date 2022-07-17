from sqlalchemy.orm import sessionmaker, Session
from bot.db.engine import engine

session: Session = sessionmaker(bind=engine)()
