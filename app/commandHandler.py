import re
from vk_api.longpoll import Event, VkLongPoll
import vk_api
from typing import List, Optional

from config import settings
from create_tables import get_session, engine
import add
import vkSend
import update
import get
import copyToSpreadsheet


# TODO by new structure
# # args = [{text.title}, {text.attachments}]
# def add_attachments(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
#     if len(args) < 2 or not args[0] or not args[1]:
#         return 1
# 
#     params = {'title': args[0]}
# 
#     # Подключение к БД
#     session = get_session(engine)
# 
#     text = session.query(Text).filter_by(**params).first()
# 
#     if not text:
#         #завершение работы в БД
#         session.close()
# 
#         return 2
# 
#     existing_attachments = json.loads(text.attachments)
#     new_attachments = {'name': [*existing_attachments]}
# 
#     for arg in args[1].split(', '):
#         if session.query(Attachment).filter_by(name=arg).first():
#             new_attachments['name'].append(arg)
# 
#     if not new_attachments['name']:
#         #завершение работы в БД
#         session.close()
# 
#         return 8
# 
#     text.attachments = json.dumps(new_attachments['name'])
# 
#     # Завершение работы в БД
#     session.commit()
#     session.close()
# 
#     return 0
# 
# 
# # args = [{text.title}, {text.attachments}]
# def delete_attachments_by_id(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
#     if len(args) < 2 or not args[0] or not args[1]:
#         return 1
# 
#     params = {'title': args[0]}
# 
#     # Подключение к БД
#     session = get_session(engine)
# 
#     text = session.query(Text).filter_by(**params).first()
# 
#     if not text:
#         #завершение работы в БД
#         session.close()
# 
#         return 2
# 
#     existing_attachments = json.loads(text.attachments)
#     edited_attachments = {'name': []}
# 
#     if sorted(args[1].split(', ')) == sorted(existing_attachments):
#         text.attachments = json.dumps([])
# 
#         #завершение работы в БД
#         session.commit()
#         session.close()
# 
#         return 0
# 
#     for attach in existing_attachments:
#         if attach not in args[1].split(', '):
#             edited_attachments['name'].append(attach)
# 
#     if not edited_attachments['name']:
#         #завершение работы в БД
#         session.close()
# 
#         return 8
# 
#     text.attachments = json.dumps(edited_attachments['name'])
# 
#     # Завершение работы в БД
#     session.commit()
#     session.close()
# 
#     return 0
# 
# # args = [{text.title}]
# def delete_attachments(event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
#     if len(args) < 1 or not args[0]:
#         return 1
# 
#     params = {'title': args[0]}
# 
#     # Подключение к БД
#     session = get_session(engine)
# 
#     text = session.query(Text).filter_by(**params).first()
# 
#     text.attachments = json.dumps([])
# 
#     #завершение работы в БД
#     session.commit()
#     session.close()
# 
#     return 0

class Handler:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=settings.VK_BOT_TOKEN)
        self.longpoll = VkLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        self.session = get_session(engine)

    def new_title(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return add.title_entry(self.vk, self.session, event, args)

    def load(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return add.attachment_entry(self.vk, self.session, event, args)

    def send_message(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return vkSend.messages(self.vk, self.session, event, args)

    def update_text(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return update.text_entry(self.vk, self.session, event, args)

    def update_attachment(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return update.text_attachment_entry(self.vk, self.session, event, args)

    def update_text_step(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return update.text_step_entry(self.vk, self.session, event, args)

    def update_user_step(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return update.user_step_entry(self.vk, self.session, event, args)

    def get_commands(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return get.command_entries(self.vk, self.session, event, args)

    def update_user_admin(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return update.user_admin_entry(self.vk, self.session, event, args)

    def check(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return vkSend.unreceived_messages(self.vk, self.session, event, args)

    def get_texts(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return get.text_entries(self.vk, self.session, event, args)

    def get_steps(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return get.step_entries(self.vk, self.session, event, args)

    def get_users(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return get.user_entries(self.vk, self.session, event, args)

    def copy_text(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.text_from_db(self.vk, self.session, event, args)

    def copy_user(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.user_from_db(self.vk, self.session, event, args)

    def copy_step(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.step_from_db(self.vk, self.session, event, args)

    def copy_attachment(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.attachment_from_db(self.vk, self.session, event, args)

    def copy_command(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.command_from_db(self.vk, self.session, event, args)

    def copy(self, event: Optional[Event] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.all_from_db(self.vk, self.session, event, args)
