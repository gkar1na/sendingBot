#!/usr/bin/env python
# coding: utf-8

import sending, change, check, config
from database import *
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import logging


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

# Оповещение необработанным диалогам
for dialog in vk.messages.getDialogs(unanswered=1)['items']:

    # Попытка обработать диалог
    try:
        sending.message(
            vk=vk,
            ID=dialog['message']['user_id'],
            message=config.unread_text
        )

    # Если возникнет непредвиденная ошибка
    except Exception as e:
        message = f'{datetime.now()} - "{e}"'

        # Отправить мне сообщение об ошибке
        sending.message(
            vk=vk,
            ID=config.my_id,
            message=message
        )

# Зацикливание запуска прослушки после исключений
while True:

    # Попытка запустить прослушку
    try:

        # Запуск прослушки
        for event in longpoll.listen():

            # Если пришло новое сообщение сообществу:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:

                # Добавление нового юзера в бд и отправка текста ПРИВЕТСТВИЕ
                if event.user_id not in get_users():
                    add_users({event.user_id})
                    sending.message(
                        vk=vk,
                        ID=event.user_id if event.from_user else event.chat_id,
                        message=get_text('ПРИВЕТСТВИЕ_2')
                    )

                # Если нет текста в полученном сообщении, то отправить текст ОШИБКА с кнопкой связи
                if not event.text:
                    message = config.problem_message + \
                              f'vk.com/{get_km_domain(get_domain(event.user_id))}'
                    sending.error_message(
                        vk=vk,
                        ID=event.user_id if event.from_user else event.chat_id,
                        message=message
                    )
                    continue

                # Если ввели какую-то команду и есть права админа:
                if check.permission(config.orginizers, event.user_id) and event.text[0] in {'/', '!', '.'}:

                    # Разделение текста сообщения на команду и ее аргументы
                    text = list(map(str, event.text.split()))
                    command = text[0][1:]
                    try:
                        args = text[1:]
                    except IndexError:
                        args = []

                    # Если команда существует:
                    if command in config.commands.keys():

                        # Отправить подтверждение начала выполнения команды
                        sending.message(
                            vk=vk,
                            ID=event.user_id if event.from_user else event.chat_id,
                            message=f'Вызвана команда "{command}" с аргументами {args}'
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

                            # Если параметры верные и это индивидуальная рассылка
                            if domains:
                                # Отправить сообщение каждому пользователю
                                message = get_text(key)
                                for domain in domains:
                                    sending.message(
                                        vk=vk,
                                        ID=get_id(domain),
                                        message=message
                                    )

                                # Уведомление об успешном завершении рассылки
                                sending.message(
                                    vk=vk,
                                    ID=event.user_id,
                                    message=f'Рассылка отправлена'
                                )

                            # Если параметры есть и они верные:
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
                                message = event.text[
                                              event.text.find(f'/{command} {key} {permission} ') +
                                              3 +
                                              len(command) +
                                              len(key) +
                                              len(str(permission)):
                                          ]
                            except Exception as e:
                                print(f'{datetime.now()} - "{e}"')
                                message = ''

                            # Если параметры есть и они верные:
                            if key and permission != -100 and message:

                                # Запуск изменения текста
                                result = change.text(
                                    admin=event.user_id,
                                    key=key,
                                    message=message,
                                    permission=permission
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
                                message = event.text[
                                              event.text.find(f'/{command} {key} {permission} ') +
                                              3 +
                                              len(command) +
                                              len(key) +
                                              len(str(permission)):
                                          ]
                            except Exception as e:
                                print(f'{datetime.now()} - "{e}"')
                                message = ''

                            # Если параметры есть и они верные:
                            if key and permission != -100 and message:

                                # Запуск добавления текста
                                add_texts(
                                    {
                                        key: [permission, message]
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
                                domain = args[1]
                            except IndexError:
                                domain = ''

                            # Если параметры есть и они верные:
                            if km_link and domain:

                                # Запуск изменения КМа
                                result = change.km_domain(
                                    km_limk=km_link,
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
                                domain = args[0]
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

                        # ИНФО_КМ km_domain(домен кма)
                        elif check.permission(config.orginizers, event.user_id) and config.commands[command] == 6:

                            # Попытка считать все нужные параметры
                            try:
                                km_domain = args[0]
                            except IndexError:
                                km_domain = ''

                            # Если параметры есть и они верные:
                            if km_domain in get_domains():

                                # Формирование списка юзеров КМа
                                message = f'К КМу vk.com/{km_domain} относятся:'
                                for km_user in get_km_users(km_domain):
                                    message += '\nvk.com/' + km_user

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
                                domain = args[0]
                            except IndexError:
                                domain = ''

                            # Если параметры есть и они верные:
                            if domain in get_domains():

                                # Получение данных о юзере
                                km_domain, km_chat_id, name, surname, domain = get_user_info(domain)

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
                                message = f'Текст рассылки "{key}":\n\n"{get_text(key)}"'

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
                                message=get_text('КОМАНДЫ')
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
                            message=f'Не сущесвует команды "{command}" с аргументами {args}'
                        )

                # Если юзер обратился к своему КМу:
                elif event.text == 'Сообщить о проблеме':

                    # Получение информации о юзере
                    km_domain, km_chat_id, name, surname, domain = get_user_info(get_domain(event.user_id))

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
                                    message=get_text(f'ПЕРЕХОД{permission - 1}')
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

    # Если возникнет непредвиденная ошибка подключения:
    except Exception as e:
        message = f'{datetime.now()} - "{e}"'
        print(f'{datetime.now()} - "{e}"')
