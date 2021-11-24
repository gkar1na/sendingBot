#!/usr/bin/env python
# coding: utf-8

from vk_api.longpoll import Event
import vk_api
from typing import List, Optional
import json
from sqlalchemy import desc
from sqlalchemy.orm import Session

from create_tables import Text, User, Step, Command
import sending as send


# args = [quantity]
def command_entries(vk: vk_api.vk_api.VkApiMethod,
                    session: Session,
                    event: Optional[Event] = None,
                    args: Optional[List[str]] = None) -> int:
    """ The function of getting commands from the Command table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if session.query(User).filter_by(chat_id=event.message['from_id']).first().admin:
        params = {}
    else:
        params = {'admin': False}

    commands = [{
        'name': command.name,
        'arguments': json.loads(command.arguments)
    } for command in session.query(Command).filter_by(**params)]

    if args:
        if not args[0].isdigit():
            return 9
        params['quantity'] = int(args[0])

    if params and 'quantity' in params.keys() and params['quantity'] < len(commands):
        # commands = sorted(commands, key=lambda i: i['date'], reverse=True)[:params['quantity']]
        commands = commands[:params['quantity']]
    commands = sorted(commands, key=lambda command: command['name'])

    message_texts = []
    if not commands:
        message_text = 'У вас нет доступных команд.'
    else:
        message_text = ''
        for i, command in enumerate(commands):
            if i and i % 50 == 0:
                message_texts.append(message_text)
                message_text = ''
            message_text += f'\n{i + 1}) !{command["name"]}'
            for arg in command['arguments']:
                message_text += f' <{arg}>'

    message_texts.append(message_text)
    for message_text in message_texts:
        send.message(
            vk=vk,
            chat_id=event.message['from_id'],
            text=message_text
        )

    session.commit()
    return 0


# args = [quantity]
def text_entries(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[Event] = None,
                 args: Optional[List[str]] = None) -> int:
    """ The function of getting texts from the Text table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if args[0].isdigit():
            params['quantity'] = int(args[0])
        else:
            return 9

    texts = [{
        'title': text.title,
        'step': text.step,
        'attachment': text.attachments,
        'text': text.text,
        'date': text.date
    } for text in session.query(Text).filter(Text.date != None)]

    if params and 'quantity' in params.keys() and params['quantity'] < len(texts):
        texts = sorted(texts, key=lambda text: text['date'], reverse=True)[:params['quantity']]
    texts = sorted(texts, key=lambda text: text['title'])

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
            chat_id=event.message['from_id'],
            text=message_text
        )

    session.commit()
    return 0


# args = [quantity]
def step_entries(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[Event] = None,
                 args: Optional[List[str]] = None) -> int:
    """ The function of getting steps from the Step table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if not args[0].isdigit():
            return 9
        params['quantity'] = int(args[0])

    steps = [{
        'number': step.number,
        'name': step.name,
        'date': step.date
    } for step in session.query(Step).filter(Step.date != None)]

    if params and 'quantity' in params.keys() and params['quantity'] < len(steps):
        steps = sorted(steps, key=lambda step: step['date'], reverse=True)[:params['quantity']]
    steps = sorted(steps, key=lambda step: step['number'])

    message_texts = []
    if not steps:
        message_text = 'Список шагов пуст.'
    else:
        message_text = ''
        for i, step in enumerate(steps):
            if i and i % 50 == 0:
                message_texts.append(message_text)
                message_text = ''
            message_text += f'{step["number"]}) {step["name"]}\n'

    message_texts.append(message_text)
    for message_text in message_texts:
        send.message(
            vk=vk,
            chat_id=event.message['from_id'],
            text=message_text)

    session.commit()
    return 0


# args = [quantity]
def user_entries(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[Event] = None,
                 args: Optional[List[str]] = None) -> int:
    """ The function of getting users from the User table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """

    params = {}
    if args:
        if not args[0].isdigit():
            return 9
        params['quantity'] = int(args[0])

    users = session.query(User).filter(User.chat_id != event.message['from_id'])
    if params and 'quantity' in params.keys() and params['quantity'] < users.count():
        users = users.order_by(desc(User.date)).limit(params['quantity'])

    message_texts = []
    if not users.count():
        message_text = f'Пользователей в базе нет.'
    else:
        message_text = f'Сейчас есть информация о {users.count()} пользователях:\n\n'
        steps = {step.number: step.name for step in session.query(Step)}
        titles = {text.text_id: text.title for text in session.query(Text)}
        for i, user in enumerate(users):
            if i and i % 5 == 0:
                message_texts.append(message_text)
                message_text = ''
            step = 'без шага' if user.step not in steps.keys() else f'{steps[user.step]} - {user.step}'
            message_text += f'{i + 1}) {user.first_name} {user.last_name} - vk.com/{user.domain}\n- Шаг - {step}\n'
            texts = json.loads(user.texts)
            if not texts:
                message_text += '- Нет полученных текстов.\n\n'
            else:
                message_text += '- Полученные тексты - '
                for j, text in enumerate(texts):
                    if text not in titles.keys():
                        texts.pop(j)
                message_text += '; '.join(sorted({f'"{titles[text]}"' for text in texts})) + '\n\n'

    message_texts.append(message_text)
    for message_text in message_texts:
        send.message(
            vk=vk,
            chat_id=event.message['from_id'],
            text=message_text
        )

    session.commit()
    return 0
