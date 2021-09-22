#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import logging
from database import *
from config import file_id
import os

# Подключение логов
logging.basicConfig(
    filename='bot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)

db_logger = logging.getLogger('pony.orm')
db_logger.setLevel(logging.ERROR)


def make_domain(link: str) -> str:
    if link.rfind('/') == -1:
        if link.rfind('@') == -1:
            index = -1
        else:
            index = link.rfind('@')
    else:
        index = link.rfind('/')

    domain = link[index + 1:]

    return domain


def get_creds(creds_file_name: str) -> Credentials:
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive']

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file_name, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def get_rowData(spreadsheet_id: str, ranges: str) -> list:
    creds = get_creds('credentials.json')

    service = build('sheets', 'v4', credentials=creds)

    include_grid_data = True

    request = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=ranges, includeGridData=include_grid_data)
    response = request.execute()

    rowData = response['sheets'][0]['data'][0]['rowData'][1:]

    return rowData


def get_rooms(my_domain: str) -> dict:
    rowData = get_rowData(
        spreadsheet_id=file_id,
        ranges='A:AC'  # диапазон читаемых столбцов
    )

    existing_domains = get_domains()

    rooms = {}

    for row in rowData:

        try:
            values = row['values']  # [5]['formattedValue']

            if values[22] and 'formattedValue' in values[22].keys():
                link = values[22]['formattedValue']
                link = ''.join(link.split())
            else:
                link = '-'

            if link == '-':
                continue

            domain = make_domain(link)

            if domain not in existing_domains:
                continue

            permission = get_permission(domain)

            if permission == -100:
                continue

            try:

                km_domain = get_km_domain(domain)

                if values[5] and 'formattedValue' in values[5].keys():
                    room_number = values[5]['formattedValue']
                else:
                    room_number = 'КОМНАТА НЕ НАЗНАЧЕНА'

                if km_domain == my_domain:
                    rooms.update([(domain, room_number)])

            except Exception as e:
                message = f'{datetime.now()} - "{e}" - {domain}'
                rooms.update([(domain, message)])

        except Exception as e:
            pass

    return rooms
