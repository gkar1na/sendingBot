#!/usr/bin/env python
# coding: utf-8

from database import *
from datetime import datetime
import check

@db_session
def permission(first_name: str, last_name: str, permission: int, admin=0) -> str:
    """Меняет уровень доступа пользователя.
    Принимает айди нужного пользователя и уровень, который ему присвоить.
    Если запрос от другого пользователя, то принимает его айди.
    Возвращает информативное сообщение о результаты выполнения запроса."""
    if check.permission({0}, admin):
        user_id = get(user.chat_id for user in User if user.first_name == first_name and user.last_name == last_name)
        existing_users_id = set(select(user.chat_id for user in User))

        if user_id in existing_users_id:
            key = get(user.id for user in User if user_id == user.chat_id)
            User[key].permission = permission
            User[key].date = datetime.now().strftime(date_format)
            process = f'have changed permission in User[{key}]'
        else:
            process = 'person is not found'
    else:
        process = 'no needed permission'

    return process


@db_session
def text(admin: int, key: str, message: str, permission: int) -> str:
    exiting_keys = set(select(text.key for text in Text))

    if check.permission({0}, admin):
        if key in exiting_keys:
            ID = get(text.id for text in Text if text.key == key)
            Text[ID].key = key
            Text[ID].message = message
            Text[ID].permission = permission
            Text[ID].date = datetime.now().strftime(date_format)
            process = f'have changed Text[{ID}]'
        else:
            process = 'text is not found'
    else:
        process = 'no needed permission'

    return process

@db_session
def km_domain(km_limk: str, first_name: str, last_name: str) -> str:
    exiting_first_names = set(select(user.first_name for user in User))
    exiting_last_names = set(select(user.last_name for user in User))

    if first_name in exiting_first_names and last_name in exiting_last_names:
        ID = get(user.id for user in User if user.first_name == first_name and user.last_name == last_name)
        User[ID].km_domain = km_limk
        User[ID].date = datetime.now().strftime(date_format)
        process = f'have changed User[{ID}]'
    else:
        process = 'user is not found'

    return process
