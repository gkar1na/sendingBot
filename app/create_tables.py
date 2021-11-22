from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
import json

from config import settings


# Создание движка
db = declarative_base()
engine = create_engine(settings.DB_PATH, pool_size=1000)


# Таблица с шагами
class Step(db):
    __tablename__ = 'step'

    number = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    date = Column(DateTime)


# Таблица с вложениями
class Attachment(db):
    __tablename__ = 'attachment'

    name = Column(String, primary_key=True)


# Таблица пользователей
class User(db):
    __tablename__ = 'vk_user'

    chat_id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    step = Column(Integer, ForeignKey('step.number', onupdate='cascade', ondelete='cascade'))
    texts = Column(String)
    admin = Column(Boolean)
    lectures = Column(String)
    date = Column(DateTime)


# Таблица с текстами
class Text(db):
    __tablename__ = 'text'

    text_id = Column(Integer, primary_key=True, autoincrement=True)
    step = Column(Integer, ForeignKey('step.number', onupdate='cascade', ondelete='cascade'))
    title = Column(String, unique=True)
    text = Column(String)
    attachments = Column(String)
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
    add_default()


# Создание сессии
def get_session(engine: Engine) -> Session:
    return sessionmaker(bind=engine)()


# Добавление стандартных данных
def add_default():
    session = get_session(engine)

    steps = session.query(Step)
    texts = session.query(Text)
    commands = session.query(Command)

    step_numbers = {step.number for step in steps}
    step_names = {step.name for step in steps}

    text_titles = {text.title for text in texts}
    text_steps = {text.step for text in texts}

    command_names = {command.name for command in commands}

    for step in json.loads(settings.STEPS):
        if (
                step['number'] not in step_numbers and
                step['name'] not in step_names
        ):
            session.add(Step(**step))

    for text in json.loads(settings.TEXTS):
        if (
                text['title'] not in text_titles and
                text['step'] not in text_steps
        ):
            session.add(Text(**text))

    for command in json.loads(settings.COMMANDS):
        if (
                command['name'] not in command_names
        ):
            command['arguments'] = json.dumps(command['arguments'])
            session.add(Command(**command))

    session.commit()
    session.close()


# Удаление таблиц
def delete_tables():
    Command.__table__.drop(engine)
    Text.__table__.drop(engine)
    User.__table__.drop(engine)
    Step.__table__.drop(engine)


if __name__ == "__main__":
    create_tables(engine)
    add_default()
