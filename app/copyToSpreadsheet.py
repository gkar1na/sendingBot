#!/usr/bin/env python
# coding: utf-8

from vk_api.longpoll import Event
import vk_api
from typing import List, Optional
from sqlalchemy.orm import Session
from validate_email import validate_email
from datetime import datetime

from create_tables import Text, User, Step, Command, Attachment
from sheetsParser import Spreadsheet
import updateSheet
import sending as send


# args = [email]
def text_from_db(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[Event] = None,
                 args: Optional[List[str]] = None) -> int:
    """ The function of creating a spreadsheet with data from the Text table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if not validate_email(args[0]):
            return 9
        params['email'] = args[0]

    spreadsheet = Spreadsheet()
    spreadsheet.create(title=f'Имеющиеся в БД тексты на {datetime.now()}',
                       sheet_title='Text')

    if params:
        spreadsheet.share_with_email_for_writing(params['email'])
    else:
        spreadsheet.share_with_anybody_for_writing()

    updateSheet.text_cells(spreadsheet, session.query(Text))

    send.message(
        vk=vk,
        chat_id=event.message['from_id'],
        text=spreadsheet.get_sheet_url()
    )

    session.commit()
    return 0


# args = [email]
def user_from_db(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[Event] = None,
                 args: Optional[List[str]] = None) -> int:
    """ The function of creating a spreadsheet with data from the User table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if not validate_email(args[0]):
            return 9
        params['email'] = args[0]

    spreadsheet = Spreadsheet()
    spreadsheet.create(title=f'Имеющиеся в БД пользователи на {datetime.now()}',
                       sheet_title='User')

    if params:
        spreadsheet.share_with_email_for_writing(params['email'])
    else:
        spreadsheet.share_with_anybody_for_writing()

    updateSheet.user_cells(spreadsheet, session.query(User))

    send.message(
        vk=vk,
        chat_id=event.message['from_id'],
        text=spreadsheet.get_sheet_url()
    )

    session.commit()
    return 0


# args = [email]
def step_from_db(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[Event] = None,
                 args: Optional[List[str]] = None) -> int:
    """ The function of creating a spreadsheet with data from the Step table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if not validate_email(args[0]):
            return 9
        params['email'] = args[0]

    spreadsheet = Spreadsheet()
    spreadsheet.create(title=f'Имеющиеся в БД шаги на {datetime.now()}',
                       sheet_title='Step')

    if params:
        spreadsheet.share_with_email_for_writing(params['email'])
    else:
        spreadsheet.share_with_anybody_for_writing()

    updateSheet.step_cells(spreadsheet, session.query(Step))

    send.message(
        vk=vk,
        chat_id=event.message['from_id'],
        text=spreadsheet.get_sheet_url()
    )

    session.commit()
    return 0


# args = [email]
def attachment_from_db(vk: vk_api.vk_api.VkApiMethod,
                       session: Session,
                       event: Optional[Event] = None,
                       args: Optional[List[str]] = None) -> int:
    """ The function of creating a spreadsheet with data from the Attachment table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if not validate_email(args[0]):
            return 9
        params['email'] = args[0]

    spreadsheet = Spreadsheet()
    spreadsheet.create(title=f'Имеющиеся в БД вложения на {datetime.now()}',
                       sheet_title='Attachment')

    if params:
        spreadsheet.share_with_email_for_writing(params['email'])
    else:
        spreadsheet.share_with_anybody_for_writing()

    updateSheet.attachment_cells(spreadsheet, session.query(Attachment))

    send.message(
        vk=vk,
        chat_id=event.message['from_id'],
        text=spreadsheet.get_sheet_url()
    )

    session.commit()
    return 0


# args = [email]
def command_from_db(vk: vk_api.vk_api.VkApiMethod,
                    session: Session,
                    event: Optional[Event] = None,
                    args: Optional[List[str]] = None) -> int:
    """ The function of creating a spreadsheet with data from the Command table in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if not validate_email(args[0]):
            return 9
        params['email'] = args[0]

    spreadsheet = Spreadsheet()
    spreadsheet.create(title=f'Имеющиеся в БД команды на {datetime.now()}',
                       sheet_title='Command')

    if params:
        spreadsheet.share_with_email_for_writing(params['email'])
    else:
        spreadsheet.share_with_anybody_for_writing()

    updateSheet.command_sells(spreadsheet, session.query(Command))

    send.message(
        vk=vk,
        chat_id=event.message['from_id'],
        text=spreadsheet.get_sheet_url()
    )

    session.commit()
    return 0


# args = [email]
def all_from_db(vk: vk_api.vk_api.VkApiMethod,
                session: Session,
                event: Optional[Event] = None,
                args: Optional[List[str]] = None) -> int:
    """ The function of creating a spreadsheet with data from all tables in DB.

    :param vk: session for connecting to VK API
    :param session: session to connect to the database
    :param event: event object in VK
    :param args: arguments of the command entered

    :return: error number or 0
    """
    params = {}
    if args:
        if not validate_email(args[0]):
            return 9
        params['email'] = args[0]

    spreadsheet = Spreadsheet()
    spreadsheet.create(title=f'Имеющиеся в БД данные на {datetime.now()}',
                       sheet_title='User')
    updateSheet.user_cells(spreadsheet, session.query(User))
    spreadsheet.add_sheet(sheet_title='Text')
    updateSheet.text_cells(spreadsheet, session.query(Text))
    spreadsheet.add_sheet(sheet_title='Command')
    updateSheet.command_sells(spreadsheet, session.query(Command))
    spreadsheet.add_sheet(sheet_title='Step')
    updateSheet.step_cells(spreadsheet, session.query(Step))
    spreadsheet.add_sheet(sheet_title='Attachment')
    updateSheet.attachment_cells(spreadsheet, session.query(Attachment))

    send.message(
        vk=vk,
        chat_id=event.message['from_id'],
        text=spreadsheet.get_spreadsheet_url()
    )

    session.commit()
    return 0
