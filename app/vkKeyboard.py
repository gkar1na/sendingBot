#!/usr/bin/env python
# coding: utf-8

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api

def get_user_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = vk_api.keyboard.VkKeyboard(inline=True)
    keyboard.add_callback_button(label='Информация',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['Info'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Сообщить о проблеме',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['Problem'])

    return keyboard

def get_admin_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = vk_api.keyboard.VkKeyboard(inline=True)
    keyboard.add_callback_button(label='Вызов команд',
                                 color=VkKeyboardColor.POSITIVE,
                                 payload=['Commands'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Информация',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['Info'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Сообщить о проблеме',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['Problem'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Выключить бота',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['Turn off'])

    return keyboard