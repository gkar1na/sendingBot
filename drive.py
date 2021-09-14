#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import logging
import config, change, database, sending
from database import *
import os

os.chdir(config.drive_path)

# Подключение логов
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

db_logger = logging.getLogger('pony.orm')
db_logger.setLevel(logging.WARNING)


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']


def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    from googleapiclient import discovery

    service = discovery.build('sheets', 'v4', credentials=creds)

    # Айти таблицы
    spreadsheet_id = config.file_id

    # Диапазон читаемых столбцов
    ranges = ['A:AC']

    include_grid_data = True

    request = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=ranges, includeGridData=include_grid_data)
    response = request.execute()

    rowData = response['sheets'][0]['data'][0]['rowData'][1:]

    existing_domains = database.get_domains()

    for row in rowData:
        values = row['values']

        link = values[22]['formattedValue']
        link = ''.join(link.split())

        if link.rfind('/') == -1:
            if link.rfind('@') == -1:
                index = -1
            else:
                index = link.rfind('@')
        else:
            index = link.rfind('/')

        domain = link[index + 1:]

        if domain not in existing_domains:
            continue

        permission = database.get_permission(domain)

        if permission == -100:
            continue

        try:
            if permission == 1:
                try:
                    # Подключение к сообществу
                    vk_session = vk_api.VkApi(token=config.TOKEN)
                    vk = vk_session.get_api()

                    # Отправка уведомления об успешном переходе
                    sending.message(
                        vk=vk,
                        ID=get_id(domain),
                        message=get_text('ПЕРЕХОД1'),
                        attachment=get_attachment('ПЕРЕХОД1')
                    )

                    # Изменение уровня в БД
                    change.permission(
                        domain=domain,
                        permission=2
                    )

                    km_domain, km_chat_id, name, surname = get_user_info(domain)

                    sending.message(
                        vk=vk,
                        ID=km_chat_id,
                        message=f'Пользователь vk.com/{domain} зарегистрировался'
                    )

                except Exception as e:
                    message = f'{datetime.now()} - "{e}"'
                    with open('bot.log', 'a') as file:
                        print(message, file=file)

            if permission == 2 and \
                    values[3] and 'formattedValue' in values[3].keys() and values[3]['formattedValue'] == '1':
                try:
                    # Подключение к сообществу
                    vk_session = vk_api.VkApi(token=config.TOKEN)
                    vk = vk_session.get_api()

                    # Отправка уведомления об успешном переходе
                    sending.message(
                        vk=vk,
                        ID=get_id(domain),
                        message=get_text('ПЕРЕХОД2'),
                        attachment=get_attachment('ПЕРЕХОД2')
                    )

                    # Изменение уровня в БД
                    change.permission(
                        domain=domain,
                        permission=3
                    )

                    km_domain, km_chat_id, name, surname = get_user_info(domain)

                    sending.message(
                        vk=vk,
                        ID=km_chat_id,
                        message=f'Пользователь vk.com/{domain} оплатил'
                    )

                except Exception as e:
                    message = f'{datetime.now()} - "{e}"'
                    with open('bot.log', 'a') as file:
                        print(message, file=file)

        except Exception as e:
            print(f'{datetime.now()} - "{e}" - {domain}')


if __name__ == '__main__':
    main()
