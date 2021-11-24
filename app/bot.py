import subprocess
import sys
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import vk_api
import time
from datetime import datetime
import json
import logging
import re

from config import settings
from create_tables import engine, get_session, User, Text, Command
import sending
import commandHandler


# Подключение к сообществу
vk_session = vk_api.VkApi(token=settings.VK_BOT_TOKEN)
longpoll = VkBotLongPoll(vk=vk_session, group_id=settings.GROUP_ID)
vk = vk_session.get_api()


def start():
    errors = {
        -1: 'Неизвестная ошибка.',
        1: 'Недостаточно аргументов.',
        2: 'Такого текста не существует.',
        3: 'Такой текст уже существует.',
        4: 'Такого шага не существует.',
        5: 'Такого пользователя не существует.',
        6: 'Существуют только значения "True" и "False" (регистр не важен)',
        7: 'Вложение не прикреплено.',
        8: 'Такого вложения не существует.',
        9: 'Неправильные параметры.',
        10: 'Текст с таким заголовком не заполнен.'
    }

    # Подключение логов
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    assert subprocess.call([sys.executable, 'create_tables.py']) == 0

    # Текст сообщения для необработанных диалогов
    message = settings.UNREAD_MESSAGE_TEXT

    # Оповещение необработанным диалогам
    for dialog in vk.messages.getDialogs(unanswered=1)['items']:

        # Айди пользователя
        chat_id = dialog['message']['user_id']

        # Попытка отправить сообщение
        try:
            sending.message(
                vk=vk,
                chat_id=chat_id,
                text=message
            )

        # Оповещение о недошедшем сообщении
        except Exception as e:
            # Подключение к БД
            session = get_session(engine)
            user = session.query(User).filter_by(chat_id=chat_id).first()
            if user:
                message = f'Пользователю vk.com/{user.domain} ({chat_id}) не отправилось сообщение по причине: "{e}"'
                sending.message(
                    vk=vk,
                    chat_id=settings.MY_VK_ID,
                    text=message
                )
            session.close()

    # Зацикливание запуска прослушки после возможных исключений
    while True:

        # Попытка запустить прослушку
        try:
            logger.info('Бот запущен')

            # Запуск прослушки
            for event in longpoll.listen():

                # Если пришло новое сообщение сообществу:
                if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
                    logger.info(f'Получено сообщение от chat_id="{event.message["from_id"]}": "{event.message["text"]}"')

                    # Подключение к БД
                    session = get_session(engine)

                    # Добавление нового пользователя в БД и отправка приветственного сообщения, если пользователь новый
                    if event.message['from_id'] not in {i[0] for i in session.query(User.chat_id).all()}:
                        # Получение информации о пользователе
                        user_info = vk.users.get(user_id=event.message['from_id'], fields='domain')
                        user_info = user_info[0]
                        user = User(
                            chat_id=event.message['from_id'],
                            domain=user_info['domain'],
                            first_name=user_info['first_name'],
                            last_name=user_info['last_name'],
                            step=1,
                            texts=json.dumps([]),
                            admin=False,
                            lectures=json.dumps([]),
                            date=datetime.now()
                        )
                        session.add(user)
                        logger.info(f'Добавлен пользователь: '
                                    f'chat_id="{event.message["from_id"]}", '
                                    f'link=vk.com/{user_info["domain"]}')

                        text_welcome = session.query(Text).filter_by(title=settings.TITLE_WELCOME).first()
                        if text_welcome:
                            text_welcome_attachments = [] if not text_welcome.attachments \
                                else json.loads(text_welcome.attachments)
                            sending.message(
                                vk=vk,
                                chat_id=event.message['from_id'],
                                text=text_welcome.text,
                                attachments=text_welcome_attachments
                            )
                            texts = json.loads(user.texts)
                            texts.append(text_welcome.text_id)
                            user.texts = json.dumps(texts)
                        del text_welcome

                        sending.message(
                            vk=vk,
                            chat_id=settings.MY_VK_ID,
                            text=f'Пользователь vk.com/{user_info["domain"]} ({event.message["from_id"]}) написал боту.'
                        )

                    # Сохранение возможных изменений в БД
                    session.commit()

                    # Если в полученном сообщении нет текста, то игнорировать
                    if not event.message['text']:

                        # Завершение работы с БД
                        session.close()

                        # Задержка от спама
                        time.sleep(settings.DELAY)

                        continue

                    # Если ввели текстовое сообщение, то игнорировать:
                    if event.message['text'][0] not in {'/', '!', '.'}:

                        # Завершение работы с БД
                        session.commit()
                        session.close()

                        # Задержка от спама
                        time.sleep(settings.DELAY)

                        continue

                    # Разделение текста сообщения на команду
                    words = list(map(str, event.message['text'].split()))
                    command = words[0][1:].lower()
                    logger.info(f'user_id="{event.message["from_id"]}" вызвал команду "{command}"')

                    # Если ввели несуществующую команду:
                    if not session.query(Command).filter_by(name=command).first():
                        sending.message(
                            vk=vk,
                            chat_id=event.message['from_id'],
                            text='Такой команды не существует.'
                        )

                        continue

                    # Если есть необходимые права:
                    if (session.query(User).filter_by(chat_id=event.message['from_id']).first().admin or
                            not session.query(Command).filter_by(name=command).first().admin):

                        # Отправить подтверждение начала выполнения команды
                        sending.message(
                            vk=vk,
                            chat_id=event.message['from_id'],
                            text=f'Вызвана команда:\n{command}. Начинаю выполнять...'
                        )

                        # Разделение текста сообщения на аргументы команды, если они введены
                        args = re.findall('<(.*?)>', event.message['text'], re.DOTALL)

                        # Обработчик команд:
                        response = -1
                        handler = commandHandler.Handler()

                        # new_title "{text.title}"
                        if command == 'new_title':
                            response = handler.new_title(event, args)
                            # response = vkCommandHandler.new_next(event, args)

                        # load
                        elif command == 'load':
                            response = handler.load(event, args)

                        # send_message "{text.title}" "OPTIONALLY: {step.number} | {step.name}"
                        elif command == 'send_message':
                            response = handler.send_message(event, args)

                        # update_text "{text.title}" "text.text"
                        elif command == 'update_text':
                            response = handler.update_text(event, args)

                        # update_attachment "{text.title}" "{text.attachments}"
                        elif command == 'update_attachment':
                            response = handler.update_attachment(event, args)

                        # add_text_attachments "{text.title}" "{text.attachments}"
                        elif command == 'add_text_attachments':
                            response = handler.add_text_attachments(event, args)

                        # delete_text_attachments "{text.title}" "{text.attachments}"
                        elif command == 'delete_text_attachments':
                            response = handler.delete_text_attachments(event, args)

                        # delete_attachments "{text.title}"
                        elif command == 'clear_text_attachments':
                            response = handler.clear_text_attachments(event, args)

                        # update_text_step "{text.title}" "{step.number} | {step.name}"
                        elif command == 'update_text_step':
                            response = handler.update_text_step(event, args)

                        # update_user_step "{user.chat_id} | {user.domain}" "{step.number} | {step.name}"
                        elif command == 'update_user_step':
                            response = handler.update_user_step(event, args)

                        # get_commands
                        elif command == 'get_commands':
                            response = handler.get_commands(event, args)

                        # update_user_admin "{user.domain}" "{user.admin}"
                        elif command == 'update_user_admin':
                            response = handler.update_user_admin(event, args)

                        # check
                        elif command == 'check':
                            response = handler.check(event, args)

                        # get_texts
                        elif command == 'get_texts':
                            response = handler.get_texts(event, args)

                        # get_steps
                        elif command == 'get_steps':
                            response = handler.get_steps(event, args)

                        # get_users
                        elif command == 'get_users':
                            response = handler.get_users(event, args)

                        # copy_texts
                        elif command == 'copy_text':
                            response = handler.copy_text(event, args)

                        # copy_users
                        elif command == 'copy_user':
                            response = handler.copy_user(event, args)

                        # copy_step
                        elif command == 'copy_step':
                            response = handler.copy_step(event, args)

                        # copy_attachment
                        elif command == 'copy_attachment':
                            response = handler.copy_attachment(event, args)

                        # copy_command
                        elif command == 'copy_command':
                            response = handler.copy_command(event, args)

                        # copy
                        elif command == 'copy':
                            response = handler.copy(event, args)

                        handler.session.close()
                        del handler

                        if response:

                            # Отправить уведомление о некорректном завершении работы команды
                            sending.message(
                                vk=vk,
                                chat_id=event.message['from_id'],
                                text=f'=== Команда "{command}" не выполнена. ===\n'
                                     f'{errors[response]}\n'
                                     f'========================================='
                            )

                            # Завершение работы в БД
                            session.commit()
                            session.close()

                            # Задержка от спама
                            time.sleep(settings.DELAY)

                            continue

                        # Отправить уведомление об успешном завершении работы команды
                        sending.message(
                            vk=vk,
                            chat_id=event.message['from_id'],
                            text='Команда успешно выполнена.'
                        )

                        # Завершение работы в БД
                        session.commit()
                        session.close()

                        # Задержка от спама
                        time.sleep(settings.DELAY)

                    # Сообщение о вызове недоступной команды
                    else:
                        sending.message(
                            vk=vk,
                            chat_id=event.message['from_id'],
                            text=f'Недостаточно прав.'
                        )

                # Задержка от спама
                time.sleep(settings.DELAY)

        # Запись в консоль об ошибке с подключением
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    start()
