# !/usr/bin/env python
# coding: utf-8


from pony.orm import *
from datetime import datetime
import config

date_format = '%d.%m.%y %H:%M:%S'

db = Database()


class User(db.Entity):
    chat_id = Required(int)
    permission = Required(int)
    KMLink = Required(str)
    date = Required(str)

class Text(db.Entity):
    permission = Required(int)
    key = Required(str)
    message = Required(str)
    date = Required(str)


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
set_sql_debug(True)
db.generate_mapping(create_tables=True)


@db_session
def add_users(users: set) -> None:  # {chat_id}
    old_users = set(select(user.chat_id for user in User))
    old_admins = set(select(user.chat_id for user in User if user.permission == 0))

    for user in users | config.admins:
        if user not in old_users:
            admin = int(not (user in config.admins | old_admins))
            User(
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


add_users(config.admins)
add_texts(config.texts)

commit()
