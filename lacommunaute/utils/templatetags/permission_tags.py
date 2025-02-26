from django.template import Library

from lacommunaute.forum_conversation.shortcuts import can_moderate_post


register = Library()


@register.simple_tag(takes_context=True)
def user_can_moderate_post(context, user):
    return can_moderate_post(user)
