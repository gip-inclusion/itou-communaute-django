"""
    Forum member shortcuts
    ======================

    This module defines shortcut functions allowing to easily get forum member information.

"""


def get_forum_member_display_name(user):
    lastname = ""
    firstname = ""

    if user.last_name:
        lastname = f"{user.last_name.capitalize()[0]}."

    if user.first_name:
        firstname = user.first_name.capitalize()

    return " ".join([firstname, lastname]).strip()
