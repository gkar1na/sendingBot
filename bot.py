#!/usr/bin/env python
# coding: utf-8

import vk_api
import datetime
import config, sending, change, check
from database import *


vk_session = vk_api.VkApi(token=config.TOKEN)

from vk_api.longpoll import VkLongPoll, VkEventType

longpoll = VkLongPoll(vk_session)

vk = vk_session.get_api()

# Оповещение необработанным диалогам
for dialog in vk.messages.getDialogs(unanswered=1)['items']:
    sending.message(
        vk=vk,
        ID=dialog['message']['user_id'],
        message=config.unread_text
    )

# Запуск прослушки
for event in longpoll.listen():

    # Если пришло новое сообщение сообществу:
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        # Добавление нового чата в бд
        if event.user_id not in get_users():
            if event.text != config.start_text:
                sending.message(
                    vk=vk,
                    ID=event.user_id if event.from_user else event.chat_id,
                    message=f'Не выполнены какие-то условия'
                )
                continue
            elif event.user_id not in get_users():
                add_users({event.user_id})
                sending.message(
                    vk=vk,
                    ID=event.user_id if event.from_user else event.chat_id,
                    message=get_text('ПРИВЕТСТВИЕ')
                )

        # Если ввели какую-то команду
        if check.permission(config.orginizers, event.user_id) and event.text[0] in {'/', '!', '.'}:

            # Разделение текста сообщения на команду и ее аргументы
            text = list(map(str, event.text.split()))
            command = text[0][1:]

            try:
                args = text[1:]
            except IndexError:
                args = []

            # Если команда существует, то отправить подтверждение начала выполнения команды
            if command in config.commands.keys():
                sending.message(
                    vk=vk,
                    ID=event.user_id if event.from_user else event.chat_id,
                    message=f'Вызвана команда "{command}" с аргументами {args} в '
                    f'{datetime.now().strftime("%H:%M")}'
                )

                # Обработчик команд
                # РАССЫЛКА key(название рассылки) permission(кому отправить)
                if check.permission(config.orginizers, event.user_id) and config.commands[command] == 1:

                    try:
                        key = args[0]
                    except:
                        key = 0

                    try:
                        permission = int(args[1])
                    except:
                        permission = -1

                    if key in get_keys() and permission != -1:
                        sending.default_sending(
                            vk=vk,
                            key=key,
                            permission=permission
                        )
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Рассылка отправлена'
                        )

                    else:
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Неверно введена команда'
                        )

                # ИЗМЕНИТЬ_ТЕКСТ key(название рассылки) permission(кому можно его отправлять) message(текст сообщения)
                elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 2:
                    try:
                        key = args[0]
                    except:
                        key = 0

                    try:
                        permission = int(args[1])
                    except:
                        permission = -1

                    try:
                        message = ' '.join(args[2:])
                    except:
                        message = ''

                    if key and permission != -1 and message:

                        result = change.text(
                            admin=event.user_id,
                            key=key,
                            message=message,
                            permission=permission
                        )

                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=result
                        )

                    else:
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Неверно введена команда'
                        )

                # ДОБАВИТЬ_ТЕКСТ key(название рассылки) permission(кому можно его отправлять) message(текст сообщения)
                elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 3:
                    try:
                        key = args[0]
                    except:
                        key = 0

                    try:
                        permission = int(args[1])
                    except:
                        permission = -1

                    try:
                        message = ' '.join(args[2:])
                    except:
                        message = ''

                    if key and permission != -1 and message:
                        add_texts({
                            key: [permission, message]
                        })

                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Добавлен новый текст рассылки "{key}"'
                        )

                    else:
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Неверно введена команда'
                        )

                # НАЗНАЧИТЬ_КМ km_link(айди КМа) first_name(имя гостя) last_name(фамилия гостя)
                elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 4:
                    try:
                        km_link = args[0]
                    except:
                        km_link = ''

                    try:
                        first_name = args[1]
                    except:
                        first_name = ''

                    try:
                        last_name = args[2]
                    except:
                        last_name = ''

                    if km_link and first_name and last_name:
                        result = change.km_domain(
                            km_limk=km_link,
                            first_name=first_name,
                            last_name=last_name
                        )

                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=result
                        )

                    else:
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Неверно введена команда'
                        )

                # ИЗМЕНИТЬ_ПРАВА first_name(имя гостя) last_name(фамилия гостя) permission(новый уровень)
                elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 5:
                    try:
                        first_name = args[0]
                    except:
                        first_name = ''

                    try:
                        last_name = args[1]
                    except:
                        last_name = ''

                    try:
                        permission = int(args[2])
                    except:
                        permission = -1

                    if first_name and last_name and permission != -1:
                        result = change.permission(
                            first_name=first_name,
                            last_name=last_name,
                            permission=permission,
                            admin=event.user_id
                        )

                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=result
                        )

                    else:
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Неверно введена команда'
                        )

                else:
                    sending.message(
                        vk=vk,
                        ID=event.user_id if event.from_user else event.chat_id,
                        message=f'Вызвана несуществующая команда "{command}" (или недостаточно прав) с аргументами'
                        f'{args} в {datetime.now().strftime("%H:%M")}'
                    )

            else:
                sending.message(
                    vk=vk,
                    ID=event.user_id,
                    message=f'Не сущесвует команды "{command}" с аргументами {args}'
                )

        # Если ввели текстовое сообщение, то перевести дальше или направить к личному КМу
        else:
            codes = get_codes(event.user_id)
            try:
                code = int(event.text)
                if code in codes:
                    level = codes.index(code)
                    permission = get_permission(event.user_id)
                    if level + 1 == permission:
                        permission += 1
                        user_info = vk.users.get(user_id=event.user_id)
                        user_info = user_info[0]
                        result = change.permission(
                            first_name=user_info['first_name'],
                            last_name=user_info['last_name'],
                            permission=permission
                        )
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Поздравляю! Ты успешно прошёл {permission-1} этап.\n' +
                                    get_text(str(permission-1))
                        )


                    else:
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message='Что-то неправильно. ' + config.problem_message +
                                    'vk.com/' + get_km_domain(event.user_id)
                        )

                else:
                    sending.message(
                        vk=vk,
                        ID=event.user_id,
                        message='Что-то неправильно. ' + config.problem_message +
                                    'vk.com/' + get_km_domain(event.user_id)
                    )
            except:
                sending.message(
                    vk=vk,
                    ID=event.user_id,
                    message=config.problem_message +
                            'vk.com/' + get_km_domain(event.user_id)
                )
