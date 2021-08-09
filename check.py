#!/usr/bin/env python
# coding: utf-8

from database import *


@db_session
def permission(needed_permissions: set, user_id: int) -> bool:
    permission = get(user.permission for user in User if user_id == user.chat_id)

    return permission in needed_permissions
