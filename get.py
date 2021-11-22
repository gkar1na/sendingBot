#!/usr/bin/env python
# coding: utf-8

from vk_api.longpoll import Event, VkLongPoll
import vk_api
from typing import List, Optional
from datetime import datetime
import json
from sqlalchemy import desc, asc
from validate_email import validate_email
from sheetsParser import Spreadsheet
import time
from sqlalchemy.orm import Session

from config import settings
from create_tables import get_session, engine, Text, User, Step, Command, Attachment
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

    if session.query(User).filter_by(chat_id=event.user_id).first().admin:
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
        send.message(vk=vk,
                     ID=event.user_id,
                     message=message_text)

    session.commit()
    return 0

