#!/usr/bin/env python
# coding: utf-8

from vk_api.bot_longpoll import VkBotEvent
import vk_api
from typing import List, Optional
import json
from sqlalchemy.orm import Session

from create_tables import Text, User, Step
import sending as send


# args = [text.title, None | step.name | step.number]
def messages(vk: vk_api.vk_api.VkApiMethod,
             session: Session,
             event: Optional[VkBotEvent] = None,
             args: Optional[List[str]] = None) -> int:
    """ The function of launching mailing in VK.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if not args or not args[0]:
        return 1

    params = {'title': args[0]}

    text = session.query(Text).filter_by(**params).first()
    if not text:
        return 2
    if not text.text and not text.attachments:
        return 10

    params = {}
    if len(args) > 1 and args[1].isdigit():
        params['step'] = int(args[1])
    elif len(args) > 1 and args[1]:
        step = session.query(Step).filter_by(name=args[1]).first()
        if not step:
            return 4
        params['step'] = step.number
    elif str(text.step).isdigit():
        params['step'] = text.step

    for user in session.query(User).filter_by(**params):
        texts = json.loads(user.texts)
        if text.text_id not in texts:
            send.message(
                vk=vk,
                chat_id=user.chat_id,
                text=text.text,
                attachments=json.loads(text.attachments)
            )
            texts.append(text.text_id)
            user.texts = json.dumps(texts)

    session.commit()
    return 0


# args = []
def unreceived_messages(vk: vk_api.vk_api.VkApiMethod,
                        session: Session,
                        event: Optional[VkBotEvent] = None,
                        args: Optional[List[str]] = None) -> int:
    """ The function of launching mailing of all unreceived messages to VK.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    users = session.query(User)
    texts = session.query(Text)
    for user in users:
        user_texts = set([] if not user.texts else json.loads(user.texts))
        for text in texts:
            if text.text_id not in user_texts and text.step and text.step <= user.step:
                send.message(
                    vk=vk,
                    chat_id=user.chat_id,
                    text=text.text,
                    attachments=[] if not text.attachments else json.loads(text.attachments))
                user_texts.add(text.text_id)
        user.texts = json.dumps(list(user_texts))
        session.commit()

    return 0
