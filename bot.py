#!/usr/bin/env python
# coding: utf-8

import vk_api
import datetime
import config, database, sending

vk_session = vk_api.VkApi(token=config.TOKEN)

from vk_api.longpoll import VkLongPoll, VkEventType

longpoll = VkLongPoll(vk_session)

vk = vk_session.get_api()

# Запуск прослушки
for event in longpoll.listen():

    # Если пришло новое сообщение сообществу:
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:

        # Добавление нового чата в бд
        if event.from_user:
            database.add_users({event.user_id})
        elif event.from_chat:
            database.add_users({event.chat_id})

        # Если ввели какую-то команду
        if event.text[0] in {'/', '!', '.'}:

            # Разделение текста сообщения на команду и ее аргументы
            text = sending.morphological_analysis(event.text)
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
                    message=f'Вызвана команда {command} с аргументами {args} в '
                    f'{datetime.datetime.now().strftime("%H:%M")}'
                )

                # Обработчик команд
                if config.commands[command] == 1:  # РАССЫЛКА key permission
                    try:
                        key = args[0]
                    except:
                        key = 0

                    try:
                        permission = int(args[1])
                    except:
                        permission = -1


                    sending.default_sending(
                        vk=vk,
                        key=key,
                        permission=int(args[0])
                    )

        # Если ввели текстовое сообщение, то направить к личному КМу
        else:
            sending.message(
                vk=vk,
                ID=event.user_id if event.from_user else event.chat_id,
                message='Если у тебя есть вопрос, пиши своему КМу: ' + sending.KMLink(event.user_id)
            )
