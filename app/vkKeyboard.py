#!/usr/bin/env python
# coding: utf-8

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api

def get_inline_keyboard() -> vk_api.keyboard.VkKeyboard:

    return vk_api.keyboard.VkKeyboard(inline=True)

def get_user_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Информация',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['info'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Сообщить о проблеме',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['problem'])

    return keyboard

def get_admin_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Вызов команд',
                                 color=VkKeyboardColor.POSITIVE,
                                 payload=['command_menu'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Информация',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['info'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Сообщить о проблеме',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['problem'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Выключить бота',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['turn_off'])

    return keyboard

def get_command_menu_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Команды БД',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['bd_commands'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Команды парсера',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['parser_commands'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Команды ВК',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['vk_commands'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard

def get_bd_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Добавить',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['add'])
    keyboard.add_callback_button(label='Обновить',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['update'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Получить',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['get'])
    keyboard.add_callback_button(label='Удалить',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['delete'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard

def get_add_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Текст',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['add_text'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Вложения',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['add_attachments'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Вложения к тексту',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['add_text_attachments'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard

def get_update_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Текст',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['update_text'])
    keyboard.add_callback_button(label='Вложения к тексту',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['update_text_attachment'])
    keyboard.add_callback_button(label='Шаг',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['update_step'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Шаг юзера',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['update_user_step'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Админ',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['update_admin'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard

def get_get_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Команды',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['get_commands'])
    keyboard.add_callback_button(label='Тексты',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['get_texts'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Шаги',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['get_steps'])
    keyboard.add_callback_button(label='Юзеров',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['get_users'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard

def get_delete_bd_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Вложения к тексту',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['delete_text_attachments'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Все вложения к тексту',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['clear_text_attachmnets'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard

def get_parser_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Копировать тексты',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['copy_text'])
    keyboard.add_callback_button(label='Копировать юзеров',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['copy_user'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Копировать шаги',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['copy_step'])
    keyboard.add_callback_button(label='Копировать вложения',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['copy_attachment'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Копировать команды',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['copy_command'])
    keyboard.add_callback_button(label='Копировать всё',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['copy'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard

def get_vk_commands_keyboard() -> vk_api.keyboard.VkKeyboard:

    keyboard = get_inline_keyboard()

    keyboard.add_callback_button(label='Рассылка',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['vk_messages'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Неотправленные сообщения',
                                 color=VkKeyboardColor.PRIMARY,
                                 payload=['vk_unreceived_messages'])
    keyboard.add_line()
    keyboard.add_callback_button(label='Назад',
                                 color=VkKeyboardColor.NEGATIVE,
                                 payload=['back'])

    return keyboard