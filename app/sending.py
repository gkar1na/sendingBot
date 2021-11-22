from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
import vk_api
import time
from typing import Optional, Type, List

from config import settings
from create_tables import get_session, engine, User


def message(vk: Type[vk_api.vk_api.VkApiMethod], ID: Type[int], message: Type[str],
            keyboard: Optional[vk_api.keyboard.VkKeyboard] = None, attachment: Optional[List[str]] = None) -> None:
    """Функция, отправляющая сообщение пользователю.

    :param vk: начатая сессия ВК с авторизацией в сообществе
    :type vk: VkApiMethod

    :param ID: айди нужного пользователя
    :type ID: int

    :param message: основной текст сообщения
    :type message: str

    :param keyboard: необязательная клавиатура, которая прикрепляется к сообщению
    :type keyboard: VkKeyboard

    :param attachment: необязательное вложение в сообщение
    :type attachment: list[str]

    :return: ничего не возвращает
    :rtype: None
    """

    # Попытка отправить сообщение
    try:
        vk.messages.send(
            user_id=ID,
            message=message,
            attachment=attachment,
            random_id=get_random_id(),
            keyboard=None if not keyboard else keyboard.get_keyboard()
        )

        # Задержка от спама
        time.sleep(settings.DELAY)

    # Оповещение о недошедшем сообщении
    except Exception as e:
        session = get_session(engine)
        user = session.query(User).filter_by(chat_id=ID).first()

        if user:
            domain = session.query(User).filter_by(chat_id=ID).first().domain

            message = f'Пользователю vk.com/{domain} ({ID})' \
                      f'не отправилось сообщение "{message}"\n' \
                      f'По причине: "{e}"'
            vk.messages.send(
                user_id=settings.MY_VK_ID,
                message=message,
                random_id=get_random_id()
            )
