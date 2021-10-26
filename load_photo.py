#!/usr/bin/env python
# coding: utf-8

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import config

# Подключение к сообществу
vk_session = vk_api.VkApi(token=config.TOKEN)

longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

upload = vk_api.VkUpload(vk)
photo = upload.photo_messages('file_name')
owner_id = photo[0]['owner_id']
photo_id = photo[0]['id']
access_key = photo[0]['access_key']
attachment = f'photo{owner_id}_{photo_id}_{access_key}'

print(attachment)