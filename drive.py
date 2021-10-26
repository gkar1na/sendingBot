# #!/usr/bin/env python
# # coding: utf-8
#
# from __future__ import print_function
# import os.path
# from vk_api.longpoll import VkLongPoll, VkEventType
# import vk_api
# import logging
# import config, change, database, sending, sheets_parser
# from database import *
# import os
#
# os.chdir(config.drive_path)
#
# # Подключение логов
# logging.basicConfig(
#     filename='bot.log',
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.WARNING
# )
# logger = logging.getLogger(__name__)
#
# db_logger = logging.getLogger('pony.orm')
# db_logger.setLevel(logging.WARNING)
#
#
# def main():
#     rowData = sheets_parser.get_rowData(
#         spreadsheet_id=config.file_id,
#         ranges='A:AC'
#     )
#
#     existing_domains = database.get_domains()
#
#     for row in rowData:
#
#         try:
#             values = row['values']
#             if values[22] and 'formattedValue' in values[22].keys():
#                 link = values[22]['formattedValue']
#                 link = ''.join(link.split())
#             else:
#                 link = '-'
#
#             if link.rfind('/') == -1:
#                 if link.rfind('@') == -1:
#                     index = -1
#                 else:
#                     index = link.rfind('@')
#             else:
#                 index = link.rfind('/')
#
#             domain = link[index + 1:]
#
#             if domain not in existing_domains:
#                 continue
#
#             permission = database.get_permission(domain)
#
#             if permission == -100 or link == '-':
#                 continue
#
#             try:
#                 if permission == 1:
#                     try:
#                         # Подключение к сообществу
#                         vk_session = vk_api.VkApi(token=config.TOKEN)
#                         vk = vk_session.get_api()
#
#                         # Отправка уведомления об успешном переходе
#                         sending.message(
#                             vk=vk,
#                             ID=get_id(domain),
#                             message=get_text('ПЕРЕХОД1'),
#                             attachment=get_attachment('ПЕРЕХОД1')
#                         )
#
#                         # Изменение уровня в БД
#                         change.permission(
#                             domain=domain,
#                             permission=2
#                         )
#
#                         km_domain, km_chat_id, name, surname = get_user_info(domain)
#
#                         sending.message(
#                             vk=vk,
#                             ID=km_chat_id,
#                             message=f'Пользователь vk.com/{domain} зарегистрировался'
#                         )
#
#                     except Exception as e:
#                         message = f'{datetime.now()} - "{e}"'
#                         with open('bot.log', 'a') as file:
#                             print(message, file=file)
#
#                 if permission == 2 and \
#                         values[3] and 'formattedValue' in values[3].keys() and values[3]['formattedValue'] == '1':
#                     try:
#                         # Подключение к сообществу
#                         vk_session = vk_api.VkApi(token=config.TOKEN)
#                         vk = vk_session.get_api()
#
#                         # Отправка уведомления об успешном переходе
#                         sending.message(
#                             vk=vk,
#                             ID=get_id(domain),
#                             message=get_text('ПЕРЕХОД2'),
#                             attachment=get_attachment('ПЕРЕХОД2')
#                         )
#
#                         # Изменение уровня в БД
#                         change.permission(
#                             domain=domain,
#                             permission=3
#                         )
#
#                         km_domain, km_chat_id, name, surname = get_user_info(domain)
#
#                         sending.message(
#                             vk=vk,
#                             ID=km_chat_id,
#                             message=f'Пользователь vk.com/{domain} оплатил'
#                         )
#
#                     except Exception as e:
#                         message = f'{datetime.now()} - "{e}"'
#                         with open('bot.log', 'a') as file:
#                             print(message, file=file)
#
#             except Exception as e:
#                 message = f'{datetime.now()} - "{e}" - {domain}'
#                 with open('bot.log', 'a') as file:
#                     print(message, file=file)
#
#         except Exception as e:
#             pass
#
#
# if __name__ == '__main__':
#     main()
