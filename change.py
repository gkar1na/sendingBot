#!/usr/bin/env python
# coding: utf-8

from database import *
from datetime import datetime
import check

@db_session
def permission(user_id: int, permission: int, admin=0) -> str:
    """Меняет уровень доступа пользователя.
    Принимает айди нужного пользователя и уровень, который ему присвоить.
    Если запрос от другого пользователя, то принимает его айди.
    Возвращает информативное сообщение о результаты выполнения запроса."""
    if check.permission(0, user_id):
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

    if key in exiting_keys:
        ID = get(text.id for text in Text if text.key == key)
        Text[ID].key = key
        Text[ID].message = message
        Text[ID].permission = permission
        Text[ID].date = datetime.now().strftime(date_format)
        process = f'have changed Text[{ID}]'
    else:
        process = 'text is not found'

    return process

