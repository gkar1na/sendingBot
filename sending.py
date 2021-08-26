#!/usr/bin/env python
# coding: utf-8

from database import *
import vk_api
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


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
    users = set(select(user.chat_id for user in User if user.chat_id != 0 and
                       (permission == -1 or user.permission == permission)))
    for user in users:
        try:
            vk.messages.send(
                user_id=user,
                message=get_text(key),
                random_id=get_random_id()
            )

        except Exception as e:
            message = f'Пользователю {user} - {get_user_info(get_domain(user))} - ' \
                f'не отправилось сообщение "{get_text(key)}"\n' \
                f'По причине: "{e}"'
            vk.messages.send(
                user_id=config.my_id,
                message=message,
                random_id=get_random_id()
            )

@db_session
def unique_sending(vk: vk_api.vk_api.VkApiMethod) -> None:
    """Функция, рассылающая уникальные сообщения каждому пользователю.

    """
    users = set(select((user.chat_id, user.permission) for user in User if user.chat_id != 0))

    for user in users:
        messages = set(select(text.message for text in Text if text.permission == user[1])) or \
                  set(select(text.message for text in Text if text.permission == -1))

        for message in messages:
            try:
                vk.messages.send(
                    user_id=user[0],
                    message=message,
                    random_id=get_random_id()
                )

            except Exception as e:
                message = f'Пользователю {user[0]} - {get_user_info(get_domain(user[0]))} - ' \
                    f'не отправилось сообщение "{message}"\n' \
                    f'По причине: "{e}"'
                vk.messages.send(
                    user_id=config.my_id,
                    message=message,
                    random_id=get_random_id()
                )


def message(vk: vk_api.vk_api.VkApiMethod, ID: int, message: str, keyboard=None) -> None:
    try:
        vk.messages.send(
            user_id=ID,
            message=message,
            random_id=get_random_id(),
            keyboard=None if not keyboard else keyboard.get_keyboard()
        )

    except Exception as e:
        message = f'Пользователю {ID} - {get_user_info(get_domain(ID))} - ' \
            f'не отправилось сообщение "{message}"\n' \
            f'По причине: "{e}"'
        vk.messages.send(
            user_id=config.my_id,
            message=message,
            random_id=get_random_id()
        )


def error_message(vk: vk_api.vk_api.VkApiMethod, ID: int, message: str) -> None:
    keyboard = VkKeyboard(inline=True)
    keyboard.add_button('Сообщить о проблеме', color=VkKeyboardColor.NEGATIVE)

    try:
        vk.messages.send(
            user_id=ID,
            message=message,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )

    except Exception as e:
        message = f'Пользователю {ID} - {get_user_info(get_domain(ID))} - ' \
            f'не отправилось сообщение "{message}"\n' \
            f'По причине: "{e}"'
        vk.messages.send(
            user_id=config.my_id,
            message=message,
            random_id=get_random_id()
        )
