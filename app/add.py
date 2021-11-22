#!/usr/bin/env python
# coding: utf-8

from vk_api.longpoll import Event
import vk_api
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from create_tables import Text, Attachment
import sending as send


# args = [text.title]
def title_entry(vk: vk_api.vk_api.VkApiMethod,
                session: Session,
                event: Optional[Event] = None,
                args: Optional[List[str]] = None) -> int:
    """ The function of adding a text title to the Text table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if not args or not args[0]:
        return 1

    params = {'title': args[0]}
    if params['title'] in {text.title for text in session.query(Text)}:
        return 3

    session.add(Text(title=params['title'], date=datetime.now()))

    session.commit()
    return 0


# args = []
def attachment_entry(vk: vk_api.vk_api.VkApiMethod,
                     session: Session,
                     event: Optional[Event] = None,
                     args: Optional[List[str]] = None) -> int:
    """ The function of adding an attachment ID to the Attachment table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    if not event.attachments:
        return 7

    for attachment in vk.messages.getById(message_ids=[event.message_id])['items'][0]['attachments']:
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
            send.message(vk=vk,
                         ID=event.user_id,
                         message=f'{params["name"]}',
                         attachment=params['name'])
            continue

        session.add(Attachment(**params))
        send.message(vk=vk,
                     ID=event.user_id,
                     message=params['name'],
                     attachment=params['name'])

    session.commit()
    return 0
