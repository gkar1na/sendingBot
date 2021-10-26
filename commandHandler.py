import json

from vk_api.longpoll import Event
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from typing import List
from datetime import datetime

from database import get_session, engine, Text, User, Step
from config import date_format, TOKEN
import sending as send


# Подключение к сообществу
vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()


# args = [text.title]
def new_title(event: Event, args: List[str]) -> int:
    if not args or not args[0]:
        return 1

    # Подключение к БД
    session = get_session(engine)

    title = args[0]

    titles = {text.title for text in session.query(Text)}
    if title in titles:
        # Завершение работы в БД
        session.close()

        return 3

    session.add(Text(title=args[0], date=datetime.now()))

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [text.title, None | step.name | step.numbed]
def send_message(event: Event, args: List[str]) -> int:
    if not args or not args[0]:
        return 1

    # Подключение к БД
    session = get_session(engine)

    params = {'title': args[0]}
    if len(args) > 1 and args[1].isdigit(): params['step'] = int(args[1])
    elif len(args) > 1 and args[1]: params['step'] = session.query(Step.number).filter_by(name=args[1]).first().number

    text = session.query(Text).filter_by(**params).first()

    if text:
        for chat_id in session.query(User.chat_id):
            send.message(
                vk=vk,
                ID=chat_id[0],
                message=text.text,
                attachment=text.attachment
            )

    else:
        # Завершение работы в БД
        session.close()

        return 2

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


def update_text(event: Event, args: List[str]) -> int:

    return 0


def update_attachment(event: Event, args: List[str]) -> int:

    return 0


def update_text_step(event: Event, args: List[str]) -> int:

    return 0


def update_user_step(event: Event, args: List[str]) -> int:

    return 0
