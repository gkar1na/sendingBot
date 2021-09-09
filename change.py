#!/usr/bin/env python
# coding: utf-8

from database import *
from datetime import datetime
import check


@db_session
def permission(domain: str, permission: int, admin=0) -> str:
    """Функция, изменяющая уровень доступа пользователя в БД.

    :param domain: домен нужного пользователя
    :type domain: str

    :param permission: уровень, который присвоить этому пользователю
    :type permission: int

    :param admin: необязательный айди пользователя, от которого запрос
    :type admin: int

    :return: информативное сообщение о результате выполнения запроса
    :rtype: str
    """

    # Если запрос от пользователя с необходимым уровенем:
    if check.permission(config.admins, admin):

        # Айди пользователя
        user_id = get(user.chat_id for user in User if user.domain == domain)

        # Айди существующих пользователей
        existing_users_id = get_users()

        # Если пользователь есть в БД:
        if user_id in existing_users_id:

            # Индекс пользователя в бд
            key = get(user.id for user in User if user_id == user.chat_id)

            # Изменение уровня
            User[key].permission = permission

            # Сохранение времени изменения
            User[key].date = datetime.now().strftime(date_format)

            # Успешное выполнение запроса
            process = f'have changed permission in User[{key}]'

        # Пользователя нет в БД
        else:
            process = 'person is not found'

    # У пользователя, от которого запрос, недостаточно прав
    else:
        process = 'no needed permission'

    # Уведомление об итоге выполнения запроса
    return process


@db_session
def text(admin: int, key: str, message: str, permission: int, attachment=None) -> str:
    """Функция, изменяющая текст в БД.

    :param admin: айди пользователя, от которого запрос
    :type admin: int

    :param key: заголовок текста
    :type key: str

    :param message: новый текст
    :type message: str

    :param permission: уровень доспута, которому предназначен этот текст
    :type permission: int

    :param attachment: необязательное вложение, прикрепленное к этому тексту
    :type attachment: str

    :return: информативное сообщение о результате выполнения запроса
    :rtype: str
    """

    # Заголовки текстов, имеющиеся в БД
    exiting_keys = set(select(text.key for text in Text))

    # Если запрос от пользователя с необходимым уровенем:
    if check.permission(config.admins, admin):

        # Если текст с заданным заголовком есть в БД:
        if key in exiting_keys:

            # Индекс текста в БД
            ID = get(text.id for text in Text if text.key == key)

            # Изменение всех параметров текста
            Text[ID].key = key
            Text[ID].message = message
            Text[ID].permission = permission
            Text[ID].attachment = attachment

            # Сохранение времени изменения
            Text[ID].date = datetime.now().strftime(date_format)

            # Успешное выполнение запроса
            process = f'have changed Text[{ID}]'

        # Текста нет в БД
        else:
            process = 'text is not found'

    # У пользователя, от которого запрос, недостаточно прав
    else:
        process = 'no needed permission'

    # Уведомление об итоге выполнения запроса
    return process


@db_session
def km_domain(km_link: str, domain: str) -> str:
    """Функция, изменяющая домен КМа у пользователя в БД

    :param km_link: домен КМа
    :type km_link: str

    :param domain: домен пользователя
    :type domain: str

    :return: информативное сообщение о результате выполнения запроса
    :rtype: str
    """

    # Домены, имеющиеся в БД
    exiting_domains = get_domains()

    # Если пользователь есть в БД
    if domain in exiting_domains:

        # Индекс пользователя в БД
        ID = get(user.id for user in User if user.domain == domain)

        # Изменение домена КМа
        User[ID].km_domain = km_link

        # Сохранение времени изменения
        User[ID].date = datetime.now().strftime(date_format)

        # Успешное выполнение запроса
        process = f'have changed User[{ID}]'

    # Пользователя нет в БД
    else:
        process = 'user is not found'

    # Уведомление об итоге выполнения запроса
    return process


@db_session
def domain(old_domain: str, new_domain: str) -> str:
    """Функци, изменяющая домен пользователя в БД

    :param old_domain: старый домен
    :type old_domain: str

    :param new_domain: новый домен
    :type new_domain: str

    :return: информативное сообщение о результате выполнения запроса
    :rtype: str
    """

    # Домены, имеющиеся в БД
    exiting_domains = get_domains()

    # Если пользователь есть в БД
    if old_domain in exiting_domains:

        # Индекс пользователя в БД
        ID = get(user.id for user in User if user.domain == old_domain)

        # Изменение домена КМа
        User[ID].domain = new_domain

        # Сохранение времени изменения
        User[ID].date = datetime.now().strftime(date_format)

        # Успешное выполнение запроса
        process = f'have changed User[{ID}]'

    # Пользователя нет в БД
    else:
        process = 'user is not found'

    # Уведомление об итоге выполнения запроса
    return process
