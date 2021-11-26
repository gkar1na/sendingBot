from vk_api.bot_longpoll import VkBotEvent, VkBotLongPoll
import vk_api
from typing import List, Optional

from config import settings
from create_tables import get_session, engine
import add
import vkSend
import update
import get
import copyToSpreadsheet
import delete


class Handler:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=settings.VK_BOT_TOKEN)
        self.longpoll = VkBotLongPoll(self.vk_session)
        self.vk = self.vk_session.get_api()
        self.session = get_session(engine)

    def new_title(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return add.title_entry(self.vk, self.session, event, args)

    def load(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return add.attachment_entry(self.vk, self.session, event, args)

    def send_message(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return vkSend.messages(self.vk, self.session, event, args)

    def update_text(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return update.text_entry(self.vk, self.session, event, args)

    def update_attachment(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return update.text_attachment_entry(self.vk, self.session, event, args)

    def add_text_attachments(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return add.text_attachments(self.vk, self.session, event, args)

    def delete_text_attachments(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return delete.text_attachments(self.vk, self.session, event, args)

    def clear_text_attachments(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return delete.text_attachments_all(self.vk, self.session, event, args)

    def update_text_step(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return update.text_step_entry(self.vk, self.session, event, args)

    def update_user_step(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return update.user_step_entry(self.vk, self.session, event, args)

    def get_commands(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return get.command_entries(self.vk, self.session, event, args)

    def update_user_admin(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return update.user_admin_entry(self.vk, self.session, event, args)

    def check(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return vkSend.unreceived_messages(self.vk, self.session, event, args)

    def get_texts(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return get.text_entries(self.vk, self.session, event, args)

    def get_steps(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return get.step_entries(self.vk, self.session, event, args)

    def get_users(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return get.user_entries(self.vk, self.session, event, args)

    def copy_text(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.text_from_db(self.vk, self.session, event, args)

    def copy_user(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.user_from_db(self.vk, self.session, event, args)

    def copy_step(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.step_from_db(self.vk, self.session, event, args)

    def copy_attachment(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.attachment_from_db(self.vk, self.session, event, args)

    def copy_command(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.command_from_db(self.vk, self.session, event, args)

    def copy(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
        return copyToSpreadsheet.all_from_db(self.vk, self.session, event, args)


# class keyboardHandler(Handler):
#
#     def __int__(self):
#         Handler.__init__()
#
#     def new_title(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return add.title_entry(self.vk, self.session, event, args)
#
#     def load(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return add.attachment_entry(self.vk, self.session, event, args)
#
#     def send_message(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return vkSend.messages(self.vk, self.session, event, args)
#
#     def update_text(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return update.text_entry(self.vk, self.session, event, args)
#
#     def update_attachment(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return update.text_attachment_entry(self.vk, self.session, event, args)
#
#     def add_text_attachments(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return add.text_attachments(self.vk, self.session, event, args)
#
#     def delete_text_attachments(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return delete.text_attachments(self.vk, self.session, event, args)
#
#     def clear_text_attachments(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return delete.text_attachments_all(self.vk, self.session, event, args)
#
#     def update_text_step(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return update.text_step_entry(self.vk, self.session, event, args)
#
#     def update_user_step(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return update.user_step_entry(self.vk, self.session, event, args)
#
#     def get_commands(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return get.command_entries(self.vk, self.session, event, args)
#
#     def update_user_admin(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return update.user_admin_entry(self.vk, self.session, event, args)
#
#     def check(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return vkSend.unreceived_messages(self.vk, self.session, event, args)
#
#     def get_texts(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return get.text_entries(self.vk, self.session, event, args)
#
#     def get_steps(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return get.step_entries(self.vk, self.session, event, args)
#
#     def get_users(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return get.user_entries(self.vk, self.session, event, args)
#
#     def copy_text(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return copyToSpreadsheet.text_from_db(self.vk, self.session, event, args)
#
#     def copy_user(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return copyToSpreadsheet.user_from_db(self.vk, self.session, event, args)
#
#     def copy_step(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return copyToSpreadsheet.step_from_db(self.vk, self.session, event, args)
#
#     def copy_attachment(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return copyToSpreadsheet.attachment_from_db(self.vk, self.session, event, args)
#
#     def copy_command(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return copyToSpreadsheet.command_from_db(self.vk, self.session, event, args)
#
#     def copy(self, event: Optional[VkBotEvent] = None, args: Optional[List[str]] = None) -> int:
#         return copyToSpreadsheet.all_from_db(self.vk, self.session, event, args)