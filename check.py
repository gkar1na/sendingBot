#!/usr/bin/env python
# coding: utf-8

from database import *


@db_session
def permission(needed_permissions: set, user_id: int) -> bool:
    """Функция, проверяющая даличие необходимого уровня у заданного пользователя.

    :param needed_permissions: необходимые уровни
    :type needed_permissions: set

    :param user_id: айди нужного пользователя
    :type user_id: int

    :return: результат наличия должного уровня
    :rtype: bool
    """

    # Получение уровня пользователя
    permission = get_permission(get_domain(user_id))

    return permission in needed_permissions
