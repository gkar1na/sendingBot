#!/usr/bin/env python
# coding: utf-8

from vk_api.longpoll import Event
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
import vk_api

keyboard = vk_api.keyboard.VkKeyboard(inline=True)
keyboard.add_callback_button(label='FAQ',color=VkKeyboardColor.PRIMARY)

