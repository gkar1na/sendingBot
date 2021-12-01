#!/usr/bin/env python
# coding: utf-8

from vk_api.bot_longpoll import VkBotEvent
import vk_api
from typing import List, Optional
from sqlalchemy.orm import Session
import json

from create_tables import Text


# args = [{text.title}, {text.attachments}]
def text_attachments(vk: vk_api.vk_api.VkApiMethod,
                     session: Session,
                     event: Optional[VkBotEvent] = None,
                     args: Optional[List[str]] = None) -> int:
    """ The function of deleting an attachment IDs from the Text table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if len(args) < 2 or not args[0] or not args[1]:
        return 1

    params = {'title': args[0]}

    text = session.query(Text).filter_by(**params).first()
    if not text:
        return 2
    params['attachments'] = list(map(str, args[1].split(', ')))

    edited_attachments = []
    attachments = [] if not text.attachments else json.loads(text.attachments)

    if sorted(params['attachments']) == sorted(attachments):
        text.attachments = json.dumps([])

        session.commit()
        return 0

    for attach in attachments:
        if attach not in params['attachments']:
            edited_attachments.append(attach)

    if not edited_attachments:
        session.commit()
        return 8

    text.attachments = json.dumps(edited_attachments)

    session.commit()
    return 0


# args = [{text.title}]
def text_attachments_all(vk: vk_api.vk_api.VkApiMethod,
                         session: Session,
                         event: Optional[VkBotEvent] = None,
                         args: Optional[List[str]] = None) -> int:
    """ The function of deleting all attachment IDs from the Text table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if len(args) < 1 or not args[0]:
        return 1

    params = {'title': args[0]}

    text = session.query(Text).filter_by(**params).first()
    text.attachments = json.dumps([])

    session.commit()
    return 0
