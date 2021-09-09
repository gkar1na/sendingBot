#!/usr/bin/env python
# coding: utf-8

from database import *
import vk_api
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import time


@db_session
def default_sending(vk: vk_api.vk_api.VkApiMethod, key: str, permission=-1) -> None:
    """Функция, рассылающая определенное сообщение определенной группе пользователей.

    :param vk: начатая сессия ВК с авторизацией в сообществе
    :type vk: VkApiMethod

    :param key: заголовок нужной рассылки
    :type key: str

    :param permission: уровень доступа, которому отправить рассылку (-1 для всех)
    :type permission: int

    :return: ничего не возвращает
    :rtype: None
    """

    # Айди всех реальных пользователей
    users = set(select(user.chat_id for user in User if user.chat_id != 0 and
                       (permission == -1 or user.permission == permission)))

    # Обработка каждого пользователя
    for user in users:

        # Текст сообщения
        message = get_text(key)

        # Попытка отправить заданное сообщение
        try:
            vk.messages.send(
                user_id=user,
                message=message,
                attachment=get_attachment(key),
                random_id=get_random_id()
            )

        # Оповещение о недошедшем сообщении
        except Exception as e:
            domain = get_domain(user)
            message = f'Пользователю {user} - {get_user_info(domain)} - vk.com/{domain}' \
                f'не отправилось сообщение "{message}"\n' \
                f'По причине: "{e}"'
            vk.messages.send(
                user_id=config.my_id,
                message=message,
                random_id=get_random_id()
            )

        # Задержка от спама
        time.sleep(config.delay)


@db_session
def unique_sending(vk: vk_api.vk_api.VkApiMethod) -> None:
    """Функция, рассылающая уникальные сообщения каждому пользователю.

    :param vk: начатая сессия ВК с авторизацией в сообществе
    :type vk: VkApiMethod

    :return: ничего не возвращает
    :rtype: None
    """

    # Айди и уровень всех реальных пользователей
    users = set(select((user.chat_id, user.permission) for user in User if user.chat_id != 0))

    # Обработка каждого пользователя
    for user in users:

        # Все сообщения, предназначенные определенному пользователю
        messages = set(select((text.message, text.attachment) for text in Text if text.permission == user[1])) or \
                  set(select((text.message, text.attachment) for text in Text if text.permission == -1))

        # Обработка каждого сообщения
        for message, attachment in messages:

            # Попытка отправить сообщение
            try:
                vk.messages.send(
                    user_id=user[0],
                    message=message,
                    attachment=attachment,
                    random_id=get_random_id()
                )

            # Оповещение о недошедшем сообщении
            except Exception as e:
                domain = get_domain(user[0])
                message = f'Пользователю {user[0]} - {get_user_info(domain)} - vk.com/{domain}' \
                    f'не отправилось сообщение "{message}"\n' \
                    f'По причине: "{e}"'
                vk.messages.send(
                    user_id=config.my_id,
                    message=message,
                    random_id=get_random_id()
                )

            # Задержка от спама
            time.sleep(config.delay)


def message(vk: vk_api.vk_api.VkApiMethod, ID: int, message: str, keyboard=None, attachment=None) -> None:
    """Функция, отправляющая сообщение пользователю.

    :param vk: начатая сессия ВК с авторизацией в сообществе
    :type vk: VkApiMethod

    :param ID: айди нужного пользователя
    :type ID: int

    :param message: основной текст сообщения
    :type message: str

    :param keyboard: необязательная клавиатура, которая прикрепляется к сообщению
    :type keyboard: VkKeyboard

    :param attachment: необязательное вложение в сообщение
    :type attachment: str

    :return: ничего не возвращает
    :rtype: None
    """

    # Попытка отправить сообщение
    try:
        vk.messages.send(
            user_id=ID,
            message=message,
            attachment=attachment,
            random_id=get_random_id(),
            keyboard=None if not keyboard else keyboard.get_keyboard()
        )

    # Оповещение о недошедшем сообщении
    except Exception as e:
        domain = get_domain(ID)
        message = f'Пользователю {ID} - {get_user_info(domain)} - vk.com/{domain}' \
            f'не отправилось сообщение "{message}"\n' \
            f'По причине: "{e}"'
        vk.messages.send(
            user_id=config.my_id,
            message=message,
            random_id=get_random_id()
        )


def error_message(vk: vk_api.vk_api.VkApiMethod, ID: int, message: str, attachment=None) -> None:
    """Функция, отправляющая информационное сообщение с возможностью обратиться к КМу напрямую.

    :param vk: начатая сессия ВК с авторизацией в сообществе
    :type vk: VkApiMethod

    :param ID: айди нужного пользователя
    :type ID: int

    :param message: основной текст сообщения
    :type message: str

    :param attachment: необязательное вложение в сообщение
    :type attachment: str

    :return: ничего не возвращает
    :rtype: None
    """

    # Создание инлайн клавиатуры для обращения к КМу
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('Сообщить о проблеме', color=VkKeyboardColor.NEGATIVE)

    # Попытка отправить сообщение
    try:
        vk.messages.send(
            user_id=ID,
            message=message,
            attachment=attachment,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )

    # Оповещение о недошедшем сообщении
    except Exception as e:
        domain = get_domain(ID)
        message = f'Пользователю {ID} - {get_user_info(domain)} - vk.com/{domain}' \
            f'не отправилось сообщение "{message}"\n' \
            f'По причине: "{e}"'
        vk.messages.send(
            user_id=config.my_id,
            message=message,
            random_id=get_random_id()
        )
