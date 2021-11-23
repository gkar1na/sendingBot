#!/usr/bin/env python
# coding: utf-8

from vk_api.longpoll import Event
import vk_api
from typing import List, Optional
from sqlalchemy.orm import Session

from create_tables import Text, Attachment, Step, User
from googleParser import make_domain


# args = [{text.title}, {text.text}]
def text_entry(vk: vk_api.vk_api.VkApiMethod,
               session: Session,
               event: Optional[Event] = None,
               args: Optional[List[str]] = None) -> int:
    """ The function of updating a text from the Text table in DB.

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
    text.text = args[1]

    session.commit()
    return 0


# args = [{text.title}, {text.attachments}]
def text_attachment_entry(vk: vk_api.vk_api.VkApiMethod,
                          session: Session,
                          event: Optional[Event] = None,
                          args: Optional[List[str]] = None) -> int:
    """ The function of updating an attachment from the Text table in DB.

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
    attach_params = {'name': args[1]}
    if not session.query(Attachment).filter_by(**attach_params).first():
        return 8
    text.attachments = attach_params['name']

    session.commit()
    return 0


# args = [{text.title}, {step.number} | {step.name}]
def text_step_entry(vk: vk_api.vk_api.VkApiMethod,
                    session: Session,
                    event: Optional[Event] = None,
                    args: Optional[List[str]] = None) -> int:
    """ The function of updating an step from the Text table in DB.

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

    if args[1].isdigit():
        if int(args[1]) not in {step.number for step in session.query(Step)}:
            return 4
        params['step'] = int(args[1])
    elif args[1]:
        if args[1] not in {step.name for step in session.query(Step)}:
            return 4
        params['step'] = session.query(Step.number).filter_by(name=args[1]).first().number

    text.step = params['step']

    session.commit()
    return 0


# args = [{user.domain}, {step.number} | {step.name}]
def user_step_entry(vk: vk_api.vk_api.VkApiMethod,
                    session: Session,
                    event: Optional[Event] = None,
                    args: Optional[List[str]] = None) -> int:
    """ The function of updating an step from the User table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if len(args) < 2 or not args[0] or not args[1]:
        return 1

    params = {'domain': make_domain(args[0])}

    user = session.query(User).filter_by(**params).first()
    if not user:
        return 5

    if args[1].isdigit():
        if int(args[1]) not in {step.number for step in session.query(Step)}:
            return 4
        params['step'] = int(args[1])
    elif args[1]:
        if args[1] not in {step.name for step in session.query(Step)}:
            return 4
        params['step'] = session.query(Step.number).filter_by(name=args[1]).first().number

    user.step = params['step']

    session.commit()
    return 0


# args = [{user.domain}, {user.admin]
def user_admin_entry(vk: vk_api.vk_api.VkApiMethod,
                     session: Session,
                     event: Optional[Event] = None,
                     args: Optional[List[str]] = None) -> int:
    """ The function of updating an admin from the User table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if len(args) < 2 or not args[0] or not args[1]:
        return 1

    params = {'domain': args[0]}

    user = session.query(User).filter_by(**params).first()
    if not user:
        return 5
    if args[1].lower() == 'true':
        user.admin = True
    elif args[1].lower() == 'false':
        user.admin = False
    else:
        return 6

    session.commit()
    return 0
