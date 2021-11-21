from __future__ import print_function
import time
import json
import logging
import re

import sending as send
from sheetsParser import get_rowData
from create_tables import engine, get_session, User, Text
from config import settings


def make_domain(link: str) -> str:
    domain = re.sub(r'[@*]?|(.*vk.com/)', '', link.lower())

    return domain


def start(vk):
    while True:
        # Подключение логов
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        logger = logging.getLogger('parser')
        session = get_session(engine)
        try:
            logger.info('Парсер запущен')

            while True:
                data = get_rowData(
                    spreadsheet_id=settings.GOOGLE_TABLE_PATH,
                    ranges='A:AC'
                )

                titles = data.pop(0)

                column_domain = 0
                column_lectures = 0
                for i, title in enumerate(titles):
                    if title == 'Ссылка на ВК':
                        column_domain = i
                    elif title == 'Какие из лекций по выбору планируешь посетить?':
                        column_lectures = i

                people = []
                for i, person in enumerate(data):
                    new_person = {}
                    for j, value in enumerate(person):
                        if j == column_domain:
                            new_person['domain'] = make_domain(data[i][j])
                        elif j == column_lectures:
                            new_person['lectures'] = list(map(str, data[i][j].split(', ')))
                    people.append(new_person)

                text = session.query(Text).filter_by(title='зарегистрировался').first()
                if text:
                    for person in people:
                        user = session.query(User).filter_by(domain=person['domain']).first()
                        if user:
                            if user.lectures == '[]':

                                user.lectures = json.dumps(person['lectures'])
                                session.commit()

                                send.message(
                                    vk=vk,
                                    ID=user.chat_id,
                                    message=text.text,
                                    attachment=text.attachment
                                )

                                user.step = 2
                                session.commit()

                                texts = json.loads(user.texts)
                                texts.append(text.text_id)
                                user.texts = json.dumps(texts)

                                send.message(
                                    vk=vk,
                                    ID=settings.MY_VK_ID,
                                    message=f'Пользователь vk.com/{person["domain"]} зарегистрировался.'
                                )

                                logger.info(f'Пользователь vk.com/{person["domain"]} зарегистрировался.')

                                time.sleep(settings.DELAY)

                session.commit()

                data = get_rowData(
                    spreadsheet_id=settings.GOOGLE_TABLE_PATH2,
                    ranges='A:I'
                )

                titles = data.pop(0)

                column_domain = 0
                for i, title in enumerate(titles):
                    if title == 'Ссылка на ВК':
                        column_domain = i

                people = []
                for i, person in enumerate(data):
                    new_person = {}
                    for j, value in enumerate(person):
                        if j == column_domain:
                            new_person['domain'] = make_domain(data[i][j])
                    people.append(new_person)

                text = session.query(Text).filter_by(title='зарегистрировался на практику').first()
                if text:
                    for person in people:
                        user = session.query(User).filter_by(domain=person['domain']).first()
                        if user:
                            if user.step == 2:
                                send.message(
                                    vk=vk,
                                    ID=user.chat_id,
                                    message=text.text,
                                    attachment=text.attachment
                                )

                                user.step = 3
                                session.commit()

                                texts = json.loads(user.texts)
                                texts.append(text.text_id)
                                user.texts = json.dumps(texts)

                                send.message(
                                    vk=vk,
                                    ID=settings.MY_VK_ID,
                                    message=f'Пользователь vk.com/{person["domain"]} зарегистрировался на практику.'
                                )

                                logger.info(f'Пользователь vk.com/{person["domain"]} зарегистрировался на практику.')

                                time.sleep(settings.DELAY)

                session.commit()
                time.sleep(60)

        except Exception as e:
            session.close()
            logger.error(e)


if __name__ == '__main__':
    import bot
    start(bot.vk)
