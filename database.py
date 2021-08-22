# !/usr/bin/env python
# coding: utf-8


from pony.orm import *
from datetime import datetime
import config
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randint

# Формат вывода времени
date_format = '%d.%m.%y %H:%M:%S'

# Создание БД
db = Database()


# Создание таблицы написавших аккаунтов
class User(db.Entity):
    first_name = Required(str)
    last_name = Required(str)
    domain = Required(str)
    chat_id = Required(int)
    permission = Required(int)
    codes = Required(str)
    km_domain = Required(str)
    date = Required(str)


# Создание таблицы с текстами
class Text(db.Entity):
    permission = Required(int)
    key = Required(str)
    message = Required(str)
    date = Required(str)


# Создание таблицы  описанием уровней доступа
class Permission(db.Entity):
    key = Required(int)
    name = Required(str)
    date = Required(str)


# Открытие БД
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
set_sql_debug(True)
db.generate_mapping(create_tables=True)


@db_session
def add_users(users: set) -> None:
    """Функция добавления написавших аккаунтов в БД.
    Изначально дает уровень доступа 1, ссылку на КМа из конфига, а уникальные коды рандомно.

    :param users: айди аккаунтов
    :type users: set[int]

    :return: ничего не возвращает
    :rtype: None
    """

    # Подключение к сообществу для поиска информации о юзере
    vk_session = vk_api.VkApi(token=config.TOKEN)
    vk = vk_session.get_api()

    # Формирование списка старых юзеров
    old_users = set(select(user.chat_id for user in User))

    # Формирование списка старых админов
    old_admins = set(select(user.chat_id for user in User if user.permission == 0))

    # Перебор каждого пользователя в юзерах и админах
    for user in users | config.admins:

        # Если пользователя не было в БД:
        if user not in old_users:

            # Получение уровня доступа
            admin = int(not (user in config.admins | old_admins))

            # Получение информации о пользователе
            user_info = vk.users.get(user_id=user, fields='domain')
            user_info = user_info[0]

            # Заполнение новой строки в таблице юзеров
            User(
                first_name=user_info['first_name'],
                last_name=user_info['last_name'],
                domain=user_info['domain'],
                chat_id=user,
                permission=admin,
                codes='\n'.join([str(randint(10000000, 100000000)) for i in range(len(config.permissions) - 2)]),
                km_domain=config.km_domains[len(get_users()) % len(config.km_domains.keys())],
                date=datetime.now().strftime(date_format)
            )

            # Добавление пользователя в сет старых пользователей
            old_users.add(user)


@db_session
def add_texts(texts: dict) -> None:
    """Функция добавления текста в БД.

    :param texts: словарь с текстами, где
    ключ - строка (заголовок текста),
    значение - список, где
    целое число - уровень доступа,
    строка - сам текст.
    :type texts: dict

    :return: ничего не возвращает
    :rtype: None
    """

    # Формирование сета старых заголовков текстов
    old_keys = set(select(text.key for text in Text))

    # Перебор каждого заголовка
    for key in texts.keys():

        # Если заголовок новый:
        if key not in old_keys:

            # Заполнение новой строки в таблице текстов
            Text(
                permission=texts[key][0],
                key=key,
                message=texts[key][1],
                date=datetime.now().strftime(date_format)
            )

            # Добавление заголовка в сет старых заголовков
            old_keys.add(key)


@db_session
def add_permissions(permissions: dict) -> None:
    """Функция добавления прав доступа в БД.

    :param permissions: словарь с правами, где
    ключ - целый число (номер доступа),
    значение - строка (название уровня доступа)
    :type permissions: dict

    :return: ничего не возвращает
    :rtype: None
    """

    # Формирование сета старых названий доступов
    old_names = set(select(permission.name for permission in Permission))

    # Перевор каждого уровня доступа
    for key in permissions.keys():

        # Получение названия уровня доступа
        name = permissions[key]

        # Если названия уровня доступа новое:
        if name not in old_names:

            # Заполнение новой строки с информацией об уровне доступа в таблице
            Permission(
                key=key,
                name=name,
                date=datetime.now().strftime(date_format)
            )

            # Добаление названия уровня доступа в сет старых названий доступов
            old_names.add(name)


@db_session
def get_codes(domain: str) -> list:
    """Функция получения уникальных кодов пользователя из БД.

    :param domain: домен пользователя
    :type domain: str

    :return: список уникальных кодов
    :rtype: list[int]
    """
    return list(map(int, get(user.codes for user in User if user.domain == domain).split('\n')))


@db_session
def get_permission(domain: str) -> int:
    """Функция получения уровня доступа определенного пользователя из БД.

    :param domain: домен нужного пользователя
    :type domain: str

    :return: уровень доступа заданного пользователя
    :rtype: int
    """
    return get(user.permission for user in User if user.domain == domain)


@db_session
def get_keys() -> set:
    """Функция получения заголовков текстов из БД.

    :return: заголовки текстов
    :rtype: set[str]
    """
    return set(select(text.key for text in Text))


@db_session
def get_users() -> set:
    """Функция получения айди всех пользователей из БД.

    :return: айди всех пользователей
    :rtype: set[int]
    """
    return set(select(user.chat_id for user in User if user.chat_id != 0))


@db_session
def get_text(key: str) -> str:
    """Функция получения определенного текста из БД.

    :param key: заголовок нужного текста
    :type key: str

    :return: текст с заданным заголовком
    :rtype: str
    """
    return get(text.message for text in Text if text.key == key)


@db_session
def get_km_domain(domain: str) -> str:
    """Функция получения домена КМа определенного пользователя из БД.

    :param domain: домен нужного пользователя
    :type domain: str

    :return: домен КМа заданного пользователя
    :rtype: str
    """
    return get(user.km_domain for user in User if user.domain == domain)


@db_session
def get_domain(ID: int) -> str:
    """Функция получения домена определенного пользователя из БД.

    :param ID: айди чата нужного пользователя
    :type ID: int

    :return: домен заданного пользователя
    :rtype: str
    """
    return get(user.domain for user in User if user.chat_id == ID)


@db_session
def get_user_info(domain: str) -> tuple:
    """Функция получения информации об определенном пользователе.
    В неё входит домен его КМа, айди чата этого КМа, имя, фамилия и домен пользователя.

    :param domain: домен нужного пользователя
    :type domain: str

    :return: информация о заданном пользователе
    :rtype: tuple[str, int, str, str, str]
    """
    km_domain = get_km_domain(domain)
    km_chat_id = get(user.chat_id for user in User if user.domain == km_domain)
    name = get(user.first_name for user in User if user.domain == domain)
    surname = get(user.last_name for user in User if user.domain == domain)
    domain = domain

    return km_domain, km_chat_id, name, surname, domain


@db_session
def get_id(domain: str) -> int:
    """Функция получения айди определенного пользователя.

    :param domain: домен нужного польщователя
    :type domain: str

    :return: айди заданного пользователя
    :return: int
    """
    return get(user.chat_id for user in User if user.domain == domain)


@db_session
def get_domains() -> set:
    """Функция получения всех доменов из БД.

    :return: домены
    :rtype: set[str]
    """
    return set(select(user.domain for user in User if user.chat_id != 0))


@db_session
def get_km_users(km_domain: str) -> set:
    """Функция получения доменов юзеров определенного КМа из БД.

    :param km_domain: домен нужного КМа
    :type km_domain: str

    :return: домены юзеров заданного КМа
    :rtype: set[str]
    """
    return set(select(user.domain for user in User if user.km_domain == km_domain))


# Добавление админов из конфига в БД
add_users(config.admins)

# Добавление текстов из конфига в БД
add_texts(config.texts)

# Добавление прав доступа из конфига в БД
add_permissions(config.permissions)

# Обновление БД
commit()
