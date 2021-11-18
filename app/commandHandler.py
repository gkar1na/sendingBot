from vk_api.longpoll import Event, VkLongPoll
import vk_api
from typing import List, Optional
from datetime import datetime
import json
from sqlalchemy import desc, asc

from config import settings
from create_tables import get_session, engine, Text, User, Step, Command, Attachment
import sending as send

# Подключение к сообществу
vk_session = vk_api.VkApi(token=settings.VK_BOT_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()


# args = [text.title]
def new_title(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
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
def send_message(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
    if not args or not args[0]:
        return 1

    # Подключение к БД
    session = get_session(engine)

    params = {'title': args[0]}
    text = session.query(Text).filter_by(**params).first()

    if text:
        params = {}
        if len(args) > 1 and args[1].isdigit():
            params['step'] = int(args[1])
        elif len(args) > 1 and args[1]:
            params['step'] = session.query(Step).filter_by(name=args[1]).first().number
        elif text.step.isdigit():
            params['step'] = text.step

        for user in session.query(User).filter_by(**params):
            texts = json.loads(user.texts)

            if text.text_id not in texts:
                send.message(
                    vk=vk,
                    ID=user.chat_id,
                    message=text.text,
                    attachment=text.attachment
                )
                texts.append(text.text_id)
                user.texts = json.dumps(texts)

    else:
        # Завершение работы в БД
        session.close()

        return 2

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [{text.title}, {text.text}]
def update_text(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
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
def update_attachment(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
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

    attach_params = {'name': args[1]}

    if not session.query(Attachment).filter_by(**attach_params).first():
        # Завершение работы в БД
        session.close()

        return 8

    text.attachment = attach_params['name']

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [{text.title}, {step.number} | {step.name}]
def update_text_step(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
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
def update_user_step(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
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
def get_commands(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
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


# args = [{user.domain}, {user.admin]
def update_user_admin(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
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

    if args[1].lower() == 'true':
        user.admin = True
    elif args[1].lower() == 'false':
        user.admin = False
    else:
        # Завершение работы в БД
        session.close()

        return 6

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = []
def check(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
    # Подключение к БД
    session = get_session(engine)

    users = session.query(User)
    texts = session.query(Text)

    for user in users:
        user_texts = set(json.loads(user.texts))

        for text in texts:
            if text.text_id not in user_texts and text.step and text.step <= user.step:
                send.message(
                    vk=vk,
                    ID=user.chat_id,
                    message=text.text,
                    attachment=text.attachment
                )

                texts = json.loads(user.texts)
                texts.append(text.text_id)
                user.texts = json.dumps(texts)

        user.texts = json.dumps(list(user_texts))

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [quantity]
def get_texts(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:

    params = {}

    if args:
        if args[0].isdigit():
            params['quantity'] = int(args[0])
        else:
            return 9

    # Подключение к БД
    session = get_session(engine)

    texts = [
        {
            'title': text.title,
            'step': text.step,
            'attachment': text.attachment,
            'text': text.text,
            'date': text.date
        } for text in session.query(Text).filter(Text.date!=None)
    ]

    if params and params['quantity'] < len(texts):
        texts = sorted(texts, key=lambda i: i['date'], reverse=True)[:params['quantity']]

    texts = sorted(texts, key=lambda i: i['title'])

    message_texts = []

    if not texts:
        message_text = 'Список текстов пуст.'

    else:
        message_text = ''
        steps = {step.number: step.name for step in session.query(Step)}
        for i, text in enumerate(texts):
            if i and i % 50 == 0:
                message_texts.append(message_text)
                message_text = ''
            step = 'без шага' if text["step"] not in steps.keys() else f'{steps[text["step"]]} - {text["step"]}'
            message_text += f'{i + 1}) "{text["title"]}" ({step})\n'

    message_texts.append(message_text)
    for message_text in message_texts:
        send.message(
            vk=vk,
            ID=event.user_id,
            message=message_text
        )

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = [quantity]
def get_users(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:

    params = {}

    if args:
        if args[0].isdigit():
            params['quantity'] = int(args[0])
        else:
            return 9

    # Подключение к БД
    session = get_session(engine)

    users = session.query(User).filter(User.chat_id != event.user_id)

    if params and params['quantity'] < users.count():
        users = users.order_by(desc(User.date)).limit(params['quantity'])

    message_texts = []

    if not users.count():
        message_text = f'Пользователей в базе нет.'

    else:
        message_text = f'Сейчас есть информация о {users.count()} пользователях:\n\n'
        steps = {step.number: step.name for step in session.query(Step)}
        titles = {text.text_id: text.title for text in session.query(Text)}
        for i, user in enumerate(users):
            if i and i % 50 == 0:
                message_texts.append(message_text)
                message_text = ''
            step = 'без шага' if user.step not in steps.keys() else f'{steps[user.step]} - {user.step}'
            message_text += f'{i + 1}) {user.first_name} {user.last_name} - vk.com/{user.domain}\n- Шаг - {step}\n'
            texts = json.loads(user.texts)
            if not texts:
                message_text += '- Нет полученных текстов.\n\n'
            else:
                message_text += '- Полученные тексты - '
                message_text += '; '.join(sorted({f'"{titles[text]}"' for text in texts})) + '\n\n'

    message_texts.append(message_text)
    for message_text in message_texts:
        send.message(
            vk=vk,
            ID=event.user_id,
            message=message_text
        )

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0


# args = []
def load(event: Optional[Event] = None, args: Optional[List[str]] = None):
    if not event.attachments:
        return 7

    # Подключение к БД
    session = get_session(engine)

    attachments = vk.messages.getById(message_ids=[event.message_id])['items'][0]['attachments']

    for attachment in attachments:
        params = {}
        attach_type = attachment['type']
        if attach_type in {'photo', 'video', 'doc'}:
            attach_owner_id = attachment[attach_type]['owner_id']
            attach_id = attachment[attach_type]['id']
            attach_access_key = attachment[attach_type]['access_key']

            params = {'name': f'{attach_type}{attach_owner_id}_{attach_id}_{attach_access_key}'}

        elif attach_type == 'wall':
            attach_from_id = attachment[attach_type]['from_id']
            attach_id = attachment[attach_type]['id']

            params = {'name': f'{attach_type}{attach_from_id}_{attach_id}'}

        elif attach_type == 'audio':
            attach_owner_id = attachment[attach_type]['owner_id']
            attach_id = attachment[attach_type]['id']

            params = {'name': f'{attach_type}{attach_owner_id}_{attach_id}'}

        if session.query(Attachment).filter_by(**params).first():
            send.message(
                vk=vk,
                ID=event.user_id,
                message=f'{params["name"]}',
                attachment=params['name']
            )

            continue

        session.add(Attachment(**params))

        send.message(
            vk=vk,
            ID=event.user_id,
            message=params['name'],
            attachment=params['name']
        )

    # Завершение работы в БД
    session.commit()
    session.close()

    return 0
