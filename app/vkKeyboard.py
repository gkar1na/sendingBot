#!/usr/bin/env python
# coding: utf-8

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api
import json
from sqlalchemy.orm import Session
from vk_api.bot_longpoll import VkBotEvent, VkBotEventType
from typing import Optional, List
import re

import commandHandler
from create_tables import User, Command
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
        payload=['get_command_menu_keyboard',
                 'Теперь выберите раздел с командами\n'
                 'Для возвращения к начальному меню нажмите кнопку "Назад"']
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
        label='Выключить бота [TODO]',
        color=VkKeyboardColor.NEGATIVE,
        payload=['turn_off']
    )

    return keyboard


def get_command_menu_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Команды БД',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_bd_commands_keyboard',
                 'Теперь выберите операцию БД, которую вы хотите совершить\n'
                 'Для возвращения к разделам с командами нажмите кнопку "Назад"']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Команды парсера',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_parser_commands_keyboard',
                 'Теперь выберите операцию парсера, которую вы хотите совершить\n'
                 'Для возвращения к разделам с командами нажмите кнопку "Назад"']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Команды ВК',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_vk_commands_keyboard',
                 'Теперь выберите операцию ВК, которую вы хотите совершить\n'
                 'Для возвращения к разделам с командами нажмите кнопку "Назад"']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_admin_keyboard',
                 'Просто нажмите любую кнопку :)']
    )

    return keyboard


def get_bd_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Добавить',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_add_bd_keyboard',
                 'Теперь выберите, какую запись вы хотите добавить в БД\n'
                 'Для возвращения к выбору типа действия нажмите кнопку "Назад"']
    )
    keyboard.add_callback_button(
        label='Обновить',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_update_bd_keyboard',
                 'Теперь выберите, какую запись вы хотите обновить в БД\n'
                 'Для возвращения к выбору типа действия нажмите кнопку "Назад"']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Получить',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_get_bd_keyboard',
                 'Теперь выберите, какую запись вы хотите получить из БД\n'
                 'Для возвращения к выбору типа действия нажмите кнопку "Назад"']
    )
    keyboard.add_callback_button(
        label='Удалить',
        color=VkKeyboardColor.PRIMARY,
        payload=['get_delete_bd_keyboard',
                 'Теперь выберите, какую запись вы хотите удалить из БД\n'
                 'Для возвращения к выбору типа действия нажмите кнопку "Назад"']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_command_menu_keyboard',
                 'Теперь выберите раздел с командами\n'
                 'Для возвращения к начальному меню нажмите кнопку "Назад"']
    )

    return keyboard


def get_add_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Текст',
        color=VkKeyboardColor.PRIMARY,
        payload=['new_title']
    )
    keyboard.add_callback_button(
        label='Вложения',
        color=VkKeyboardColor.PRIMARY,
        payload=['load']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Вложения к тексту',
        color=VkKeyboardColor.PRIMARY,
        payload=['add_text_attachments']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_bd_commands_keyboard',
                 'Для возвращения к операциям БД, нажмите кнопку "Назад"']
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
        label='Шаг текста',
        color=VkKeyboardColor.PRIMARY,
        payload=['update_text_step']
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
        payload=['update_user_admin']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Вложения к тексту [TODO]',
        color=VkKeyboardColor.PRIMARY,
        payload=['update_text_attachment']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_bd_commands_keyboard',
                 'Для возвращения к операциям БД, нажмите кнопку "Назад"']
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
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_bd_commands_keyboard',
                 'Для возвращения к операциям БД, нажмите кнопку "Назад"']
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
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_bd_commands_keyboard',
                 'Для возвращения к операциям БД, нажмите кнопку "Назад"']
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
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_command_menu_keyboard',
                 'Для возвращения к разделам с командами нажмите кнопку "Назад"']
    )

    return keyboard


def get_vk_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(
        label='Рассылка',
        color=VkKeyboardColor.PRIMARY,
        payload=['send_message']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Неотправленные сообщения',
        color=VkKeyboardColor.PRIMARY,
        payload=['check']
    )
    keyboard.add_line()
    keyboard.add_callback_button(
        label='Назад',
        color=VkKeyboardColor.NEGATIVE,
        payload=['get_command_menu_keyboard',
                 'Для возвращения к разделам с командами нажмите кнопку "Назад"']
    )

    return keyboard


def required_keyboard(vk: vk_api.vk_api.VkApiMethod,
                      keyboard: str,
                      event: Optional[VkBotEvent] = None,
                      message_id: Optional[int] = None) -> int:

    chat_id = event.object['user_id']
    conversation_id = event.object['conversation_message_id']
    required_keyboard = globals()[keyboard]

    text = event.object['payload'][1]

    try:
        vk.messages.edit(
            peer_id=chat_id,
            message=text,
            message_id=message_id,
            сonversation_message_id=conversation_id,
            keyboard=required_keyboard().get_keyboard()
        )

    except Exception as e:
        message_id = sending.message(
            vk=vk,
            chat_id=chat_id,
            text=text,
            keyboard=required_keyboard()
        )

    return message_id


def required_button(vk: vk_api.vk_api.VkApiMethod,
                    session: Optional[Session],
                    keyboard: str,
                    event: Optional[VkBotEvent] = None,
                    longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None) -> int:

    button = globals()[keyboard]
    handler = commandHandler.Handler()

    response = button(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        handler=handler
    )

    handler.session.close()
    del handler

    return response


def get_popup_message(text: str) -> json:

    text = {'type': 'show_snackbar', 'text': text}

    return json.dumps(text)


def argument_handler(vk: vk_api.vk_api.VkApiMethod,
                     session: Session,
                     event: Optional[VkBotEvent] = None,
                     longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                     info: Optional[str] = None) -> List[str]:

    chat_id = event.object['user_id']

    additional_info = ''

    command_info = session.query(Command).filter_by(name=info)[0]
    command_info = json.loads(command_info.arguments)

    for command in command_info:
        additional_info += f'<{command}> '

    sending.message(
        vk=vk,
        chat_id=chat_id,
        text=f'Введите аргументы:\n{additional_info}'
        '\nДля отмены команды напишите "Отмена"'
    )

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:

            vk.messages.markAsAnsweredConversation(
                peer_id=event.object['message']['peer_id'],
                answered=1,
                group_id=settings.GROUP_ID
            )

            if event.message['text'] != 'Отмена':

                args = re.findall('<(.*?)>', event.message['text'], re.DOTALL)

                if args:

                    return args

                else:

                    sending.message(
                        vk=vk,
                        chat_id=chat_id,
                        text='Повтори ввод'
                    )

            else:

                return []


def info(vk: vk_api.vk_api.VkApiMethod,
         session: Session,
         event: Optional[VkBotEvent] = None,
         longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
         handler=None) -> int:

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
            longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
            handler=None) -> int:

    chat_id = event.object['user_id']

    sending.message(
        vk=vk,
        chat_id=chat_id,
        text='Максимально лаконично опишите свою проблему'
        '\nДля отмены напишите "Отмена"'
    )

    for keyboard_event in longpoll.listen():

        if keyboard_event.type == VkBotEventType.MESSAGE_NEW and keyboard_event.from_user:

            if keyboard_event.object['text'] != 'Отмена':

                domain = session.query(User.domain).filter_by(chat_id=chat_id).first()

                sending.message(
                    vk=vk,
                    text=f'Получено сообщение об ошибке от пользователя vk.com/{domain[0]} '
                         f'({chat_id})'
                         f'\nОписание проблемы: ' + keyboard_event.message['text'],
                    chat_id=settings.MY_VK_ID
                )

                sending.message(
                    vk=vk,
                    text='Уведомление об ошибке отправлено'
                         '\nС вами обязательно свяжутся',
                    chat_id=chat_id
                )

            else:

                sending.message(
                    vk=vk,
                    text='Команда отменена',
                    chat_id=chat_id
                )

    return 0


def load(vk: vk_api.vk_api.VkApiMethod,
         session: Session,
         event: Optional[VkBotEvent] = None,
         longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
         handler=None) -> int:

    text = 'Прикрепите вложения\n' \
           'Для отмены команды напишите "Отмена"'
    sending.message(
        vk=vk,
        chat_id=event.object['user_id'],
        text=text
    )

    handler = commandHandler.Handler()

    for new_event in longpoll.listen():

        if new_event.type == VkBotEventType.MESSAGE_NEW:

            if new_event.message['attachments']:

                response = handler.load(event=new_event)

                return response

            elif new_event.message['text'] == 'Отмена':

                sending.message(
                    vk=vk,
                    chat_id=new_event.message['from_id'],
                    text='Команда отменена'
                )

                return 0

            else:

                sending.message(
                    vk=vk,
                    chat_id=new_event.message['from_id'],
                    text='Повторите ввод'
                )


def new_title(vk: vk_api.vk_api.VkApiMethod,
              session: Session,
              event: Optional[VkBotEvent] = None,
              longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
              handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='new_title'
    )

    if not args:
        response = -2
    else:
        response = handler.new_title(event=event, args=args)

    return response


def add_text_attachments(vk: vk_api.vk_api.VkApiMethod,
                         session: Session,
                         event: Optional[VkBotEvent] = None,
                         longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                         handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='add_text_attachments'
    )

    if not args:
        response = -2
    else:
        response = handler.add_text_attachments(event=event, args=args)

    return response


def update_text(vk: vk_api.vk_api.VkApiMethod,
                session: Session,
                event: Optional[VkBotEvent] = None,
                longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='update_text'
    )

    if not args:
        response = -2
    else:
        response = handler.update_text(event=event, args=args)

    return response


def update_attachment(vk: vk_api.vk_api.VkApiMethod,
                      session: Session,
                      event: Optional[VkBotEvent] = None,
                      longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                      handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='update_attachment'
    )

    if not args:
        response = -2
    else:
        response = handler.update_attachment(event=event, args=args)

    return response


def update_text_step(vk: vk_api.vk_api.VkApiMethod,
                     session: Session,
                     event: Optional[VkBotEvent] = None,
                     longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                     handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='update_text_step'
    )

    if not args:
        response = -2
    else:
        response = handler.update_text_step(event=event, args=args)

    return response


def update_user_step(vk: vk_api.vk_api.VkApiMethod,
                     session: Session,
                     event: Optional[VkBotEvent] = None,
                     longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                     handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='update_user_step'
    )
    if not args:
        response = -2
    else:
        response = handler.update_user_step(event=event, args=args)

    return response


def update_user_admin(vk: vk_api.vk_api.VkApiMethod,
                      session: Session,
                      event: Optional[VkBotEvent] = None,
                      longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                      handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='update_user_admin'
    )

    if not args:
        response = -2
    else:
        response = handler.update_user_admin(event=event, args=args)

    return response


def delete_text_attachments(vk: vk_api.vk_api.VkApiMethod,
                            session: Session,
                            event: Optional[VkBotEvent] = None,
                            longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                            handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='delete_text_attachments'
    )

    if not args:
        response = -2
    else:
        response = handler.delete_text_attachments(event=event, args=args)

    return response


def clear_text_attachments(vk: vk_api.vk_api.VkApiMethod,
                           session: Session,
                           event: Optional[VkBotEvent] = None,
                           longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                           handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='clear_text_attachments'
    )

    if not args:
        response = -2
    else:
        response = handler.clear_text_attachments(event=event, args=args)

    return response


def get_commands(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[VkBotEvent] = None,
                 longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                 handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='get_commands'
    )

    if not args:
        response = -2
    else:
        response = handler.get_commands(event=event, args=args)

    return response


def get_texts(vk: vk_api.vk_api.VkApiMethod,
              session: Session,
              event: Optional[VkBotEvent] = None,
              longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
              handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='get_texts'
    )

    if not args:
        response = -2
    else:
        response = handler.get_texts(event=event, args=args)

    return response


def get_steps(vk: vk_api.vk_api.VkApiMethod,
              session: Session,
              event: Optional[VkBotEvent] = None,
              longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
              handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='get_steps'
    )

    if not args:
        response = -2
    else:
        response = handler.get_steps(event=event, args=args)

    return response


def get_users(vk: vk_api.vk_api.VkApiMethod,
              session: Session,
              event: Optional[VkBotEvent] = None,
              longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
              handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='get_users'
    )

    if not args:
        response = -2
    else:
        response = handler.get_users(event=event, args=args)

    return response


def copy_text(vk: vk_api.vk_api.VkApiMethod,
              session: Session,
              event: Optional[VkBotEvent] = None,
              longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
              handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='copy_text'
    )

    if not args:
        response = -2
    else:
        response = handler.copy_text(event=event, args=args)

    return response


def copy_user(vk: vk_api.vk_api.VkApiMethod,
              session: Session,
              event: Optional[VkBotEvent] = None,
              longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
              handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='copy_user'
    )

    if not args:
        response = -2
    else:
        response = handler.copy_user(event=event, args=args)

    return response


def copy_step(vk: vk_api.vk_api.VkApiMethod,
              session: Session,
              event: Optional[VkBotEvent] = None,
              longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
              handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='copy_step'
    )

    if not args:
        response = -2
    else:
        response = handler.copy_step(event=event, args=args)

    return response


def copy_attachment(vk: vk_api.vk_api.VkApiMethod,
                    session: Session,
                    event: Optional[VkBotEvent] = None,
                    longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                    handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='copy_attachment'
    )

    if not args:
        response = -2
    else:
        response = handler.copy_attachment(event=event, args=args)

    return response


def copy_command(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[VkBotEvent] = None,
                 longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                 handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='copy_command'
    )

    if not args:
        response = -2
    else:
        response = handler.copy_command(event=event, args=args)

    return response


def copy(vk: vk_api.vk_api.VkApiMethod,
         session: Session,
         event: Optional[VkBotEvent] = None,
         longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
         handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='copy'
    )

    if not args:
        response = -2
    else:
        response = handler.copy(event=event, args=args)

    return response


def send_message(vk: vk_api.vk_api.VkApiMethod,
                 session: Session,
                 event: Optional[VkBotEvent] = None,
                 longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
                 handler=None) -> int:

    args = argument_handler(
        vk=vk,
        session=session,
        event=event,
        longpoll=longpoll,
        info='send_message'
    )

    if not args:
        response = -2
    else:
        response = handler.send_message(event=event, args=args)

    return response


def check(vk: vk_api.vk_api.VkApiMethod,
          session: Session,
          event: Optional[VkBotEvent] = None,
          longpoll: Optional[vk_api.bot_longpoll.VkBotLongPoll] = None,
          handler=None) -> int:

    response = handler.check(event=event)

    return response
