from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard
import vk_api
import time
from typing import Optional, List

from config import settings
from create_tables import get_session, engine, User


def message(
        vk: vk_api.vk_api.VkApiMethod,
        chat_id: int,
        text: str,
        keyboard: Optional[vk_api.keyboard.VkKeyboard] = None,
        attachments: Optional[List[str]] = None) -> int:
    """Функция, отправляющая сообщение пользователю.

    :param vk: начатая сессия ВК с авторизацией в сообществе
    :type vk: VkApiMethod

    :param chat_id: айди нужного пользователя
    :type chat_id: int

    :param text: основной текст сообщения
    :type text: str

    :param keyboard: необязательная клавиатура, которая прикрепляется к сообщению
    :type keyboard: VkKeyboard

    :param attachments: необязательные вложения в сообщение
    :type attachments: List[str]

    :return: ничего не возвращает
    :rtype: None
    """

    message_id = 0

    # Попытка отправить сообщение
    try:
        message_id = vk.messages.send(
            user_id=chat_id,
            message=text,
            attachment=attachments,
            random_id=get_random_id(),
            keyboard=None if not keyboard else keyboard.get_keyboard()
        )

        # Задержка от спама
        time.sleep(settings.DELAY)

    # Оповещение о недошедшем сообщении
    except Exception as e:
        session = get_session(engine)
        user = session.query(User).filter_by(chat_id=chat_id).first()

        if user:
            domain = session.query(User).filter_by(chat_id=chat_id).first().domain

            text = f'Пользователю vk.com/{domain} ({chat_id})' \
                   f'не отправилось сообщение "{text}"\n' \
                   f'По причине: "{e}"'
            vk.messages.send(
                user_id=settings.MY_VK_ID,
                message=text,
                random_id=get_random_id()
            )

    return message_id
