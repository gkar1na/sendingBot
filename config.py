#!/usr/bin/env python
# coding: utf-8

TOKEN = 'TOKEN'
admins = {0}
orginizers = {0, 10}

commands = {
    'РАССЫЛКА': 1,
    'ИЗМЕНИТЬ_ТЕКСТ': 2,
    'ДОБАВИТЬ_ТЕКСТ': 3,
    'НАЗНАЧИТЬ_КМ': 4,
    'ИЗМЕНИТЬ_ПРАВА': 5,
    'ИНФО_КМ': 6,
    'ИНФО_ГОСТЬ': 7,
    'НАЗВАНИЯ_РАССЫЛОК': 8,
    'ТЕКСТ': 9,
    'КОМАНДЫ': 10,
    'ИЗМЕНИТЬ_ДОМЕН': 11,
    'ТРАНСФЕР': 12
}

texts = {

}

delay = 0.2

title_welcome = 'ПРИВЕТСТВИЕ_2'

permissions = {
    0: 'ОРГАНИЗАТОР',
    1: 'ВСТУПИЛ',
    2: 'ЗАРЕГИСТРИРОВАЛСЯ',
    3: 'ОПЛАТИЛ'
}

km_domains = {
    0: 'domain'
}

headLogin = 'vk_id'

drive_path = 'path_to_file_drive.py'

start_text = 'Начало'

problem_message = 'При возникновении вопросов пиши своему Наставнику: '

unread_text = 'Сообщения не получилось обработать, нужно отправить снова'

file_id = 'file_id'

my_id = 0

db_path = 'DB_PATH'
