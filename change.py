#!/usr/bin/env python
# coding: utf-8

from database import *

@db_session
def permission(admin: int, user_id: int, permission: int) -> str:
    """Меняет уровень доступа пользователя.
    Принимает айди нужного пользователя и уровень, который ему присвоить.
    Если запрос от другого пользователя, то принимает его айди.
    Возвращает информативное сообщение о результаты выполнения запроса."""
    existing_users_id = set(select(user.chat_id for user in User))

    if user_id in existing_users_id:
        key = get(user.id for user in User if user_id == user.chat_id)
        User[key].permission = permission
        process = 'have changed permission'
    else:
        process = 'person is not found'

    return process

