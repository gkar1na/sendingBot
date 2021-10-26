import json

from vk_api.longpoll import Event
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
from typing import List
from datetime import datetime
import json

from database import get_session, engine, Text, User, Step, Command
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
    if len(args) > 1 and args[1].isdigit():
        params['step'] = int(args[1])
    elif len(args) > 1 and args[1]:
        params['step'] = session.query(Step.number).filter_by(name=args[1]).first().number

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


# args = [{text.title}, {text.text}]
def update_text(event: Event, args: List[str]) -> int:
    if len(args) < 2 or not args[0] or not args[1]:
        return 1

    params = {'title': args[0]}

    # Подключение к БД
    session = get_session(engine)

    text = session.query(Text).filter_by(**params).first()

    if not text:
        # Завершение работы в БД
        session.close()

        return 2

    text.text = args[1]

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [{text.title}, {text.attachment}]
def update_attachment(event: Event, args: List[str]) -> int:
    if len(args) < 2 or not args[0] or not args[1]:
        return 1

    params = {'title': args[0]}

    # Подключение к БД
    session = get_session(engine)

    text = session.query(Text).filter_by(**params).first()

    if not text:
        # Завершение работы в БД
        session.close()

        return 2

    text.attachment = args[1]

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [{text.title}, {step.number} | {step.name}]
def update_text_step(event: Event, args: List[str]) -> int:
    if len(args) < 2 or not args[0] or not args[1]:
        return 1

    params = {'title': args[0]}

    # Подключение к БД
    session = get_session(engine)

    text = session.query(Text).filter_by(**params).first()

    if not text:
        # Завершение работы в БД
        session.close()

        return 2

    if args[1].isdigit():
        steps = {step.number for step in session.query(Step)}

        if int(args[1]) not in steps:
            # Завершение работы в БД
            session.close()

            return 4

        params['step'] = int(args[1])

    elif args[1]:
        step_names = {step.name for step in session.query(Step)}

        if args[1] not in step_names:
            # Завершение работы в БД
            session.close()

            return 4

        params['step'] = session.query(Step.number).filter_by(name=args[1]).first().number

    text.step = params['step']

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [{user.domain}, {step.number} | {step.name}]
def update_user_step(event: Event, args: List[str]) -> int:
    if len(args) < 2 or not args[0] or not args[1]:
        return 1

    params = {'domain': args[0]}

    # Подключение к БД
    session = get_session(engine)

    user = session.query(User).filter_by(**params).first()

    if not user:
        # Завершение работы в БД
        session.close()

        return 5

    if args[1].isdigit():
        steps = {step.number for step in session.query(Step)}

        if int(args[1]) not in steps:
            # Завершение работы в БД
            session.close()

            return 4

        params['step'] = int(args[1])

    elif args[1]:
        step_names = {step.name for step in session.query(Step)}

        if args[1] not in step_names:
            # Завершение работы в БД
            session.close()

            return 4

        params['step'] = session.query(Step.number).filter_by(name=args[1]).first().number

    user.step = params['step']

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = []
def get_commands(event: Event, args: List[str]) -> int:
    # Подключение к БД
    session = get_session(engine)

    admin = session.query(User).filter_by(chat_id=event.user_id).first().admin

    if admin:
        params = {}
    else:
        params = {'admin': False}

    commands = [
        {
            'name': command.name,
            'arguments': json.loads(command.arguments)
        } for command in session.query(Command).filter_by(**params)
    ]

    commands = sorted(commands, key=lambda i: i['name'])

    if not commands:
        message_text = 'У вас нет доступных команд.'

    else:
        message_text = 'Найдены следующие доступные команды:\n'
        for command in commands:
            message_text += f'\n!{command["name"]}'
            for arg in command['arguments']:
                message_text += f' /{arg}/'
            # message_text += '\n'

    send.message(
        vk=vk,
        ID=event.user_id,
        message=message_text
    )

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0
