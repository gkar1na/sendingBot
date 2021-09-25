#!/usr/bin/env python
# coding: utf-8

import sending, change, check, config
from database import *
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import logging
import time
import sheets_parser


# Подключение логов
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db_logger = logging.getLogger('pony.orm')
db_logger.setLevel(logging.WARNING)

# Подключение к сообществу
vk_session = vk_api.VkApi(token=config.TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

# Текст сообщения для необработанных диалогов
message = config.unread_text

# Оповещение необработанным диалогам
for dialog in vk.messages.getDialogs(unanswered=1)['items']:

    # Айди пользователя
    ID = dialog['message']['user_id']

    # Попытка отправить сообщение
    try:
        sending.message(
            vk=vk,
            ID=ID,
            message=message
        )

    # Оповещение о недошедшем сообщении
    except Exception as e:
        domain = get_domain(ID)
        message = f'Пользователю {ID} - {get_user_info(domain)} - vk.com/{domain}' \
            f'не отправилось сообщение "{message}"\n' \
            f'По причине: "{e}"'
        sending.message(
            vk=vk,
            ID=config.my_id,
            message=message
        )

# Зацикливание запуска прослушки после возможных исключений
while True:

    # Попытка запустить прослушку
    try:

        # Запуск прослушки
        for event in longpoll.listen():

            # Если пришло новое сообщение сообществу:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.from_user:

                # Добавление нового пользователя в БД и отправка приветственного сообщения, если пользователь новый
                if event.user_id not in get_users():
                    add_users({event.user_id})
                    sending.message(
                        vk=vk,
                        ID=event.user_id,
                        message=get_text(config.title_welcome),
                        attachment=get_attachment(config.title_welcome)
                    )

                    domain = get_domain(event.user_id)
                    km_domain, km_chat_id, name, surname = get_user_info(domain)

                    sending.message(
                        vk=vk,
                        ID=km_chat_id,
                        message=f'Пользователь vk.com/{domain} написал боту и определён тебе'
                    )

                # Если в полученном сообщении нет текста, то отправить информационное сообщение для обращения к КМу
                if not event.text:
                    message = config.problem_message + \
                              f'vk.com/{get_km_domain(get_domain(event.user_id))}'
                    sending.error_message(
                        vk=vk,
                        ID=event.user_id,
                        message=message
                    )

                    # Задержка от спама
                    time.sleep(config.delay)

                    # Завершение обработки сообщения
                    continue

                # Если ввели какую-то команду и есть права организатора:
                if check.permission(config.orginizers, event.user_id) and event.text[0] in {'/', '!', '.'}:

                    # Разделение текста сообщения на команду и ее аргументы, если они введены
                    words = list(map(str, event.text.split()))
                    command = words[0][1:]
                    try:
                        args = words[1:]
                    except IndexError:
                        args = []

                    # Если команда существует:
                    if command in config.commands.keys():

                        # Отправить подтверждение начала выполнения команды
                        sending.message(
                            vk=vk,
                            ID=event.user_id if event.from_user else event.chat_id,
                            message=f'Вызвана команда:\n{command}\n\nЕё агументы:\n{args}'
                        )

                        # Обработчик команд:

                        # РАССЫЛКА key(название рассылки) permission(кому отправить)
                        if check.permission(config.admins, event.user_id) and config.commands[command] == 1:

                            # Попытка считать все нужные параметры
                            domains = []
                            try:
                                key = args[0]
                            except IndexError:
                                key = 0
                            try:
                                permission = int(args[1])
                            except ValueError:
                                permission = -100
                                domains = args[1:]
                            except IndexError:
                                permission = -100

                            # Если параметры есть и это точечная рассылка
                            if domains:

                                # Отправить сообщение каждому пользователю
                                for domain in domains:
                                    sending.message(
                                        vk=vk,
                                        ID=get_id(domain),
                                        message=get_text(key),
                                        attachment=get_attachment(key)
                                    )

                                # Уведомление об успешном завершении рассылки
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Рассылка отправлена'
                                )

                            # Если параметры есть и это общая рассылка:
                            elif key in get_keys() and permission != -100:

                                # Запуск рассылки
                                sending.default_sending(
                                    vk=vk,
                                    key=key,
                                    permission=permission
                                )

                                # Уведомление об успешном завершении рассылки
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Рассылка отправлена'
                                )

                            # Если параметров нет:
                            elif not key:

                                # Запуск индивидуальной рассылки
                                sending.unique_sending(vk)

                                # Уведомление об успешном завершении рассылки
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Рассылка отправлена'
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # ИЗМЕНИТЬ_ТЕКСТ key(название рассылки) permission(кому его отправлять) message(текст сообщения)
                        elif check.permission(config.admins, event.user_id) and config.commands[command] == 2:

                            # Попытка считать все нужные параметры
                            try:
                                key = args[0]
                            except IndexError:
                                key = 0
                            try:
                                permission = int(args[1])
                            except IndexError or ValueError:
                                permission = -100
                            try:
                                attachment = args[2]
                            except IndexError:
                                attachment = ''
                            try:
                                message = event.text[
                                              event.text.find(f'/{command} {key} {permission} {attachment} ') +
                                              5 +
                                              len(command) +
                                              len(key) +
                                              len(str(permission)) +
                                              len(attachment):
                                          ]
                            except Exception as e:
                                print(f'{datetime.now()} - "{e}"')
                                message = ''

                            # Если параметры есть и они верные:
                            if key and permission != -100 and message and attachment:

                                # Запуск изменения текста
                                result = change.text(
                                    admin=event.user_id,
                                    key=key,
                                    message=message,
                                    permission=permission,
                                    attachment=attachment
                                )

                                # Уведомление о результате завершения изменения текста
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=result
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # ДОБАВИТЬ_ТЕКСТ key(название рассылки) permission(кому его отправлять) message(текст сообщения)
                        elif check.permission(config.admins, event.user_id) and config.commands[command] == 3:

                            # Попытка считать все нужные параметры
                            try:
                                key = args[0]
                            except IndexError:
                                key = 0
                            try:
                                permission = int(args[1])
                            except IndexError or ValueError:
                                permission = -100
                            try:
                                attachment = args[2]
                            except IndexError:
                                attachment = None
                            try:
                                message = event.text[
                                              event.text.find(f'/{command} {key} {permission} {attachment} ') +
                                              5 +
                                              len(command) +
                                              len(key) +
                                              len(str(permission)) +
                                              len(attachment):
                                          ]
                            except Exception as e:
                                print(f'{datetime.now()} - "{e}"')
                                message = ''

                            # Если параметры есть и они верные:
                            if key and permission != -100 and message and attachment:

                                # Запуск добавления текста
                                add_texts(
                                    {
                                        key: [permission, message, attachment]
                                    }
                                )

                                # Уведомление об успешном завершении добавления текста
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Добавлен новый текст рассылки "{key}"'
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # НАЗНАЧИТЬ_КМ km_link(домен КМа) domain(домен гостя)
                        elif check.permission(config.admins, event.user_id) and config.commands[command] == 4:

                            # Попытка считать все нужные параметры
                            try:
                                km_link = args[0]
                            except IndexError:
                                km_link = ''
                            try:
                                domain = sheets_parser.make_domain(args[1])
                            except IndexError:
                                domain = ''

                            # Если параметры есть и они верные:
                            if km_link and domain:

                                # Запуск изменения КМа
                                result = change.km_domain(
                                    km_link=km_link,
                                    domain=domain
                                )

                                # Уведомление о результате изменения КМа
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=result
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # ИЗМЕНИТЬ_ПРАВА domain(домен гостя) permission(новый уровень)
                        elif check.permission(config.admins, event.user_id) and config.commands[command] == 5:

                            # Попытка считать все нужные параметры
                            try:
                                domain = sheets_parser.make_domain(args[0])
                            except IndexError:
                                domain = ''
                            try:
                                permission = int(args[1])
                            except IndexError:
                                permission = -100

                            # Если параметры есть и они верные
                            if domain and permission != -100:

                                # Запуск изменения прав доступа
                                result = change.permission(
                                    domain=domain,
                                    permission=permission,
                                    admin=event.user_id
                                )

                                # Уведомление о результате изменения прав доступа
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=result
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # ИНФО_КМ km_domain(домен кма) permission(уровень, который вывести)
                        elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 6:

                            # Попытка считать все нужные параметры
                            try:
                                km_domain = sheets_parser.make_domain(args[0])
                            except IndexError:
                                km_domain = ''
                            try:
                                permission = int(args[1])
                            except IndexError:
                                permission = -1

                            # Если параметры есть и они верные:
                            if km_domain in get_domains():
                                # Получение словаря с комнатами
                                rooms = sheets_parser.get_rooms(km_domain)

                                # Формирование списка юзеров КМа
                                message = f'К КМу vk.com/{km_domain} относятся:'
                                number = 0
                                for km_user in get_km_users(km_domain):
                                    if permission == -1 or check.permission({permission}, get_id(km_user)):
                                        number += 1
                                        if km_user in rooms.keys():
                                            message += f'\n{number}) vk.com/{km_user} ' \
                                                f'(уровень {get_permission(km_user)}, комната {rooms[km_user]})'
                                        else:
                                            message += f'\n{number}) vk.com/{km_user} ' \
                                                f'(уровень {get_permission(km_user)})'
                                if not number:
                                    message = f'У КМа vk.com/{km_domain} никого нет, либо это не КМ'

                                # Отправка сформированного списка юзеров КМа
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=message
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # ИНФО_ГОСТЬ domain(домен гостя)
                        elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 7:

                            # Попытка считать все нужные параметры
                            try:
                                domain = sheets_parser.make_domain(args[0])
                            except IndexError:
                                domain = ''

                            # Если параметры есть и они верные:
                            if domain in get_domains():
                                # Получение данных о юзере
                                km_domain, km_chat_id, name, surname = get_user_info(domain)

                                # Формирования информационного текста о юзере
                                message = f'Инфо про гостя {name} {surname} (vk.com/{domain})\n' \
                                    f'За него отвечает vk.com/{km_domain}.\n' \
                                    f'На данный момент он находится на уровне {get_permission(domain)}'

                                # Отправка информации о юзере
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=message
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # НАЗВАНИЯ_РАССЫЛОК
                        elif check.permission(config.admins, event.user_id) and config.commands[command] == 8:

                            # Формирование списка имеющихся рассылок
                            message = f'Сейчас есть такие рассылки:'
                            for key in get_keys():
                                message += '\n' + key

                            # Отправка сформированного списка имеющихся рассылок
                            sending.message(
                                vk=vk,
                                ID=event.user_id,
                                message=message
                            )

                        # ТЕКСТ key(название рассылки)
                        elif check.permission(config.admins, event.user_id) and config.commands[command] == 9:

                            # Попытка считать все нужные параметры
                            try:
                                key = args[0]
                            except IndexError:
                                key = ''

                            # Если параметры есть и они верные:
                            if key in get_keys():

                                # Формирование сообщения с текстом
                                message = f'Вложение: {get_attachment(key)}\n' \
                                    f'Текст рассылки "{key}":\n\n"{get_text(key)}"'

                                # Отправка сообщения с текстом
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=message
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # КОМАНДЫ
                        elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 10:

                            # Отправка имеющихся команд
                            sending.message(
                                vk=vk,
                                ID=event.user_id,
                                message=get_text('КОМАНДЫ'),
                                attachment=get_attachment('КОМАНДЫ')
                            )

                        # ИЗМЕНИТЬ_ДОМЕН old_domain(старый домен) new_domain(новый домен)
                        elif check.permission(config.admins, event.user_id) and config.commands[command] == 11:

                            # Попытка считать все нужные параметры
                            try:
                                old_domain = sheets_parser.make_domain(args[0])
                            except IndexError:
                                old_domain = ''

                            try:
                                new_domain = sheets_parser.make_domain(args[1])
                            except IndexError:
                                new_domain = ''

                            # Если параметры есть и они верные:
                            if old_domain and new_domain and old_domain in get_domains():

                                # Изменение домена в БД
                                change.domain(
                                    old_domain=old_domain,
                                    new_domain=new_domain
                                )

                                message = f'У пользователя vk.com/{new_domain} изменен домен с {old_domain}'
                                # Отправка сообщения с текстом
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=message
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                     ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # ТРАНСФЕР domain(km domain)
                        elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 12:
                            # Попытка считать все нужные параметры
                            try:
                                domain = sheets_parser.make_domain(args[0])
                            except IndexError:
                                domain = ''

                            if domain:

                                transfer = sheets_parser.get_transfer(domain)

                                messages = []

                                for i, person in enumerate(transfer.keys()):
                                    messages.append(f'{i + 1}) vk.com/{person} - {transfer[person]}')

                                message = '\n'.join(messages)

                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=message
                                )

                            # Сообщение о неправильном вводе команды
                            else:
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Неверно введена команда'
                                )

                        # Сообщение о вызванной команде, которая недоступна
                        else:
                            sending.message(
                                vk=vk,
                                ID=event.user_id,
                                message=f'Недостаточно прав'
                            )

                    # Сообщение о вызове несуществующей команды
                    else:
                        sending.message(
                            vk=vk,
                            ID=event.user_id,
                            message=f'Не сущесвует такой команды'
                        )

                # Если пользователь обратился к своему КМу:
                elif event.text == 'Сообщить о проблеме':

                    # Получение информации о юзере
                    domain = get_domain(event.user_id)
                    km_domain, km_chat_id, name, surname = get_user_info(domain)

                    # Формирование сообщения КМу с данными о юзере
                    message = f'У {name} {surname} (vk.com/{domain}) возникла проблема'

                    # Отправка сформированного сообщения КМу с данными о юзере
                    sending.message(
                        vk=vk,
                        ID=km_chat_id,
                        message=message
                    )

                    # Уведомление об успешном вызове КМа
                    sending.message(
                        vk=vk,
                        ID=event.user_id,
                        message='Ждите ответа'
                    )

                # Идентификация организатора
                elif event.text == 'яорганизаторлучшегопосвята':

                    domain = get_domain(event.user_id)
                    km_domain, km_chat_id, name, surname = get_user_info(domain)

                    # Изменение уровня доступа
                    change.permission(
                        domain=domain,
                        permission=11
                    )

                    # Отправка уведомлений об успешном изменении доступа
                    sending.message(
                        vk=vk,
                        ID=event.user_id,
                        message='Поздравляю, теперь ты организатор!'
                    )
                    sending.message(
                        vk=vk,
                        ID=km_chat_id,
                        message=f'Пользователь vk.com/{domain} ({name} {surname}) теперь организатор - доступ 11'
                    )

                # Если ввели текстовое сообщение:
                else:
                    # Уникальные коды юзера
                    codes = get_codes(get_domain(event.user_id))

                    # Если это код и он правильный:
                    try:
                        # Проверка на число
                        code = int(event.text)

                        # Если число верное:
                        if code in codes:

                            # Нынешний уровень юзера
                            permission = get_permission(get_domain(event.user_id))

                            # Если есть возможность перехода:
                            if permission == 1 or permission == 2:

                                # Изменение уровня
                                permission += 1
                                result = change.permission(
                                    domain=get_domain(event.user_id),
                                    permission=permission
                                )

                                # Уведомление об успешном переходе
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=get_text(f'ПЕРЕХОД{permission - 1}'),
                                    attachment=get_attachment(f'ПЕРЕХОД{permission - 1}')
                                )

                            # Сообщить об ошибке с кнопкой связи
                            else:
                                message = config.problem_message + \
                                          f'vk.com/{get_km_domain(get_domain(event.user_id))}'
                                sending.error_message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=message
                                )

                        # Сообщить об ошибке с кнопкой связи
                        else:
                            message = config.problem_message + \
                                      f'vk.com/{get_km_domain(get_domain(event.user_id))}'
                            sending.error_message(
                                vk=vk,
                                ID=event.user_id,
                                message=message
                            )

                    # Это не код или код неверный
                    except ValueError:

                        # Отправить сообщение об ошибке с кнопкой связи
                        message = config.problem_message + \
                                  f'vk.com/{get_km_domain(get_domain(event.user_id))}'
                        sending.error_message(
                            vk=vk,
                            ID=event.user_id,
                            message=message
                        )

            # Задержка от спама
            time.sleep(config.delay)

    # Запись в консоль об ошибке с подключением
    except Exception as e:
        print(f'{datetime.now()} - "{e}"')
