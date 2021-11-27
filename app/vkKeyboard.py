#!/usr/bin/env python
# coding: utf-8

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api
import json
from sqlalchemy.orm import Session
from vk_api.bot_longpoll import VkBotEvent, VkBotLongPoll, VkBotEventType
from typing import Optional

from create_tables import User, Text, Command, Step, Attachment
import sending
from config import settings

# Загрузка кнопок, вызывающих клавиатуры ВК
keyboard_buttons = json.loads(settings.BASIC_BUTTONS)

# Загрузка кнопок, выполняющих команды
functional_buttons = json.loads(settings.FUNCTIONAL_BUTTONS)

def get_inline_keyboard() -> vk_api.keyboard.VkKeyboard:

    return vk_api.keyboard.VkKeyboard(inline=True)

def get_user_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Информация',
        color=VkKeyboardColor.PRIMARY,
        payload=['info']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Сообщить о проблеме',
        color=VkKeyboardColor.PRIMARY,
        payload=['problem']
    )

    return keyboard

def get_admin_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Вызов команд',
        color=VkKeyboardColor.POSITIVE,
        payload=['command_menu']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Информация',
        color=VkKeyboardColor.PRIMARY,
        payload=['info']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Сообщить о проблеме',
        color=VkKeyboardColor.PRIMARY,
        payload=['problem']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Выключить бота',
        color=VkKeyboardColor.NEGATIVE,
        payload=['turn_off']
    )

    return keyboard

def get_command_menu_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Команды БД',
        color=VkKeyboardColor.PRIMARY,
        payload=['bd_commands']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Команды парсера',
        color=VkKeyboardColor.PRIMARY,
        payload=['parser_commands']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Команды ВК',
        color=VkKeyboardColor.PRIMARY,
        payload=['vk_commands']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def get_bd_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Добавить',
        color=VkKeyboardColor.PRIMARY,
        payload=['add']
    )
    keyboard.add_callback_button(
        label='Обновить',
        color=VkKeyboardColor.PRIMARY,
        payload=['update']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Получить',
        color=VkKeyboardColor.PRIMARY,
        payload=['get']
    )
    keyboard.add_callback_button(
        label='Удалить',
        color=VkKeyboardColor.PRIMARY,
        payload=['delete']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def get_add_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Текст',
        color=VkKeyboardColor.PRIMARY,
        payload=['add_text']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Вложения',
        color=VkKeyboardColor.PRIMARY,
        payload=['add_attachments']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Вложения к тексту',
        color=VkKeyboardColor.PRIMARY,
        payload=['add_text_attachments']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def get_update_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Текст',
        color=VkKeyboardColor.PRIMARY,
        payload=['update_text']
    )
    keyboard.add_callback_button(
        label='Шаг',
        color=VkKeyboardColor.PRIMARY,
        payload=['update_step']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Шаг юзера',
        color=VkKeyboardColor.PRIMARY,
        payload=['update_user_step']
    )
    keyboard.add_callback_button(
        label='Админ',
        color=VkKeyboardColor.PRIMARY,
        payload=['update_admin']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Вложения к тексту',
        color=VkKeyboardColor.PRIMARY,
        payload=['update_text_attachment']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def get_get_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Команды',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_commands']
    )
    keyboard.add_callback_button(
        label='Тексты',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_texts']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Шаги',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_steps']
    )
    keyboard.add_callback_button(
        label='Юзеров',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_users']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def get_delete_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Вложения к тексту',
        color=VkKeyboardColor.PRIMARY,
        payload=['delete_text_attachments']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Все вложения к тексту',
        color=VkKeyboardColor.PRIMARY,
        payload=['clear_text_attachments']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def get_parser_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Тексты',
        color=VkKeyboardColor.PRIMARY,
        payload=['copy_text']
    )
    keyboard.add_callback_button(
        label='Юзеров',
        color=VkKeyboardColor.PRIMARY,
        payload=['copy_user']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Шаги',
        color=VkKeyboardColor.PRIMARY,
        payload=['copy_step']
    )
    keyboard.add_callback_button(
        label='Вложения',
        color=VkKeyboardColor.PRIMARY,
        payload=['copy_attachment']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Команды',
        color=VkKeyboardColor.PRIMARY,
        payload=['copy_command']
    )
    keyboard.add_callback_button(
        label='Всё',
        color=VkKeyboardColor.PRIMARY,
        payload=['copy']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def get_vk_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Рассылка',
        color=VkKeyboardColor.PRIMARY,
        payload=['vk_messages']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Неотправленные сообщения',
        color=VkKeyboardColor.PRIMARY,
        payload=['vk_unreceived_messages']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='В начало',
        color=VkKeyboardColor.NEGATIVE,
        payload=['beginning']
    )

    return keyboard

def required_keyboard(vk: vk_api.vk_api.VkApiMethod,
                      session: Session,
                      keyboard: str,
                      event: Optional[VkBotEvent] = None) -> int:

    chat_id = event.object['user_id']
    required_keyboard = globals()[keyboard_buttons[keyboard]]

    text = 'Чтобы вернуться в начало, нажми соответствующую кнопку' \
        if keyboard != 'admin' else 'Просто нажми любую кнопку :)'

    sending.message(
        vk=vk,
        chat_id=chat_id,
        text=text,
        keyboard=required_keyboard()
    )

    return 0

def info(vk: vk_api.vk_api.VkApiMethod,
         session: Session,
         event: Optional[VkBotEvent] = None) -> int:

    chat_id = event.object['user_id']

    sending.message(
        vk=vk,
        chat_id=chat_id,
        text='Чел, это Антипосвят'
    )

    return 0

def problem(vk: vk_api.vk_api.VkApiMethod,
            session: Session,
            event: Optional[VkBotEvent] = None,
            longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None) -> int:

    chat_id = event.object['user_id']

    sending.message(
        vk=vk,
        chat_id=chat_id,
        text='Максимально лаконично опишите свою проблему'
    )

    for keyboard_event in longpoll.listen():

        if keyboard_event.type == VkBotEventType.MESSAGE_NEW and keyboard_event.from_user:
            domain = session.query(User.domain).filter_by(chat_id=chat_id).first()

            sending.message(
                vk=vk,
                text=f'Получено сообщение об ошибке от пользователя vk.com/{domain[0]} ' \
                     f'({chat_id})' \
                     f'\nОписание проблемы: ' + keyboard_event.message['text'],
                chat_id=settings.MY_VK_ID
            )

            sending.message(
                vk=vk,
                text='Уведомление об ошибке отправлено' \
                     '\nС вами обязательно свяжутся',
                chat_id=chat_id
            )

            return 0