#!/usr/bin/env python
# coding: utf-8

from database import *
import vk_api
from vk_api.utils import get_random_id


@db_session
def default_sending(vk: vk_api.vk_api.VkApiMethod, key: str, permission=-1) -> None:
    """Дефолт рассылка.
    Принимает уровень, которому рассылать"""
    users = set(select(user.chat_id for user in User if user.chat_id != 0 and
                       (permission == -1 or user.permission == permission)))
    for user in users:
        vk.messages.send(
            user_id=user,
            message=get_text(key),
            random_id=get_random_id()
        )


@db_session
def unique_sending(vk: vk_api.vk_api.VkApiMethod) -> None:
    users = set(select((user.chat_id, user.permission) for user in User if user.chat_id != 0 and user.permission))

    for user in users:
        message = get(text.message for text in Text if text.permission == user[1] - 1) or \
                  get(text.message for text in Text if text.permission == -1)

        vk.messages.send(
            user_id=user[0],
            message=message,
            random_id=get_random_id()
        )


def morphological_analysis(text: str) -> list:
    """Take a string and
    return a list of all words in normal form."""
    import pymorphy2

    text = list(map(str, text.split()))

    for i in range(len(text)):
        morph = pymorphy2.MorphAnalyzer()
        text[i] = morph.parse(text[i])[0].normal_form
        text[i] = text[i].upper()
        if text[i].isdigit():
            text[i] = int(text[i])

    return text


def message(vk: vk_api.vk_api.VkApiMethod, ID: int, message: str) -> None:
    if ID >= 100000000:
        vk.messages.send(
            user_id=ID,
            message=message,
            random_id=get_random_id()
        )
    else:
        vk.messages.send(
            chat_id=ID,
            message=message,
            random_id=get_random_id()
        )
