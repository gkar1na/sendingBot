from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine

from config import db_path


# Создание движка
db = declarative_base()
engine = create_engine(db_path, pool_size=1000)


# Таблица с шагами
class Step(db):
    __tablename__ = 'step'

    number = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    date = Column(DateTime)


# Таблица пользователей
class User(db):
    __tablename__ = 'user'

    chat_id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    step = Column(Integer, ForeignKey('step.number', onupdate='cascade'))
    texts = Column(String)
    admin = Column(Boolean)
    date = Column(DateTime)


# Таблица с текстами
class Text(db):
    __tablename__ = 'text'
    text_id = Column(Integer, primary_key=True)
    step = Column(Integer, ForeignKey('step.number', onupdate='cascade'))
    title = Column(String, unique=True)
    text = Column(String)
    attachment = Column(String)
    date = Column(DateTime)


# Создание таблиц
def create_tables(engine: Engine) -> None:
    db.metadata.create_all(engine)


# Создание сессии
def get_session(engine: Engine) -> Session:
    return sessionmaker(bind=engine)()


if __name__ == "__main__":
    create_tables(engine)
    print('========== DB CREATING - OK ==========')
