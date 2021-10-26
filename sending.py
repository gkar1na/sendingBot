import vk_api
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard

from database import get_session, engine, User
from config import my_id


def message(vk: vk_api.vk_api.VkApiMethod, ID: int, message: str, keyboard=None, attachment=None) -> None:
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
    :type attachment: str

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

    # Оповещение о недошедшем сообщении
    except Exception as e:
        session = get_session(engine)
        user = session.query(User).filter_by(chat_id=ID).first()
        print(e)
        if user:
            domain = session.query(User).filter_by(chat_id=ID).first().domain

            message = f'Пользователю vk.com/{domain} ({ID})' \
                f'не отправилось сообщение "{message}"\n' \
                f'По причине: "{e}"'
            vk.messages.send(
                user_id=my_id,
                message=message,
                random_id=get_random_id()
            )
