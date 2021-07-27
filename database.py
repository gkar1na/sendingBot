# !/usr/bin/env python
# coding: utf-8


from pony.orm import *
from datetime import datetime
import config
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

date_format = '%d.%m.%y %H:%M:%S'

db = Database()


class User(db.Entity):
    first_name = Required(str)
    last_name = Required(str)
    chat_id = Required(int)
    permission = Required(int)
    KMLink = Required(str)
    date = Required(str)


class Text(db.Entity):
    permission = Required(int)
    key = Required(str)
    message = Required(str)
    date = Required(str)


class Permission(db.Entity):
    key = Required(int)
    name = Required(str)
    date = Required(str)


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
set_sql_debug(True)
db.generate_mapping(create_tables=True)


@db_session
def add_users(users: set) -> None:
    vk_session = vk_api.VkApi(token=config.TOKEN)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    old_users = set(select(user.chat_id for user in User))
    old_admins = set(select(user.chat_id for user in User if user.permission == 0))

    for user in users | config.admins:
        if user not in old_users:
            admin = int(not (user in config.admins | old_admins))
            user_info = vk.users.get(user_id=user)
            user_info = user_info[0]
            User(
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
                chat_id=user,
                permission=admin,
                KMLink='vk.com/' + config.headLogin,
                date=datetime.now().strftime(date_format)
            )
            old_users.add(user)


@db_session
def add_texts(texts) -> None:
    old_keys = set(select(text.key for text in Text))

    for key in texts.keys():
        if key not in old_keys:
            Text(
                permission=texts[key][0],
                key=key,
                message=texts[key][1],
                date=datetime.now().strftime(date_format)
            )
            old_keys.add(key)


@db_session
def add_permissions(permissions: dict) -> None:
    old_names = set(select(permission.name for permission in Permission))

    for key in permissions.keys():
        name = permissions[key]
        if name not in old_names:
            Permission(
                key=key,
                name=name,
                date=datetime.now().strftime(date_format)
            )
            old_names.add(name)


add_users(config.admins)
add_texts(config.texts)
add_permissions(config.permissions)
commit()
