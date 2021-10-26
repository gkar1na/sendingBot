import json
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
    __tablename__ = 'vk_user'

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

    text_id = Column(Integer, primary_key=True, autoincrement=True)
    step = Column(Integer, ForeignKey('step.number', onupdate='cascade'))
    title = Column(String, unique=True)
    text = Column(String)
    attachment = Column(String)
    date = Column(DateTime)


# Таблица с командами
class Command(db):
    __tablename__ = 'command'

    name = Column(String, primary_key=True)
    arguments = Column(String)
    admin = Column(Boolean)


# Создание таблиц
def create_tables(engine: Engine) -> None:
    db.metadata.create_all(engine)
    session = get_session(engine)
    # session.add(Step(number=2, name='сделал1'))
    # session.add(Text(title='title_welcome', text='Привет'))
    # session.add(Command(name='new_title', admin=True, arguments=json.dumps(['название текста'])))
    # session.add(Command(name='update_text', admin=True, arguments=json.dumps(['название текста', 'текст сообщения'])))
    # session.add(Command(name='update_attachment', admin=True, arguments=json.dumps(['название текста', 'айди вложения'])))
    # session.add(Command(name='send_message', admin=True, arguments=json.dumps(['название текста', 'ДОП.: шаг'])))
    # session.add(Command(name='update_text_step', admin=True, arguments=json.dumps(['название текста', 'новый шаг'])))
    # session.add(Command(name='update_user_step', admin=True, arguments=json.dumps(['домен', 'новый шаг'])))
    # session.add(Command(name='get_commands', admin=False, arguments=json.dumps([])))

    # session.add(Command(name='update_text', admin=True))
    # session.add(Command(name='update_text', admin=True))
    # session.add(Command(name='update_text', admin=True))
    # session.add(Command(name='update_text', admin=True))
    # session.add(Command(name='update_text', admin=True))
    # session.add(Command(name='update_text', admin=True))
    session.commit()
    session.close()

# Создание сессии
def get_session(engine: Engine) -> Session:
    return sessionmaker(bind=engine)()


if __name__ == "__main__":
    create_tables(engine)
    print('========== DB CREATING - OK ==========')
