from machina.apps.forum_conversation.admin import TopicAdmin as BaseTopicAdmin


# TODO vincentporte, need to be fixed, likers field does not appear like a raw id fields
class TopicAdmin(BaseTopicAdmin):
    raw_id_fields = (
        "poster",
        "subscribers",
        "likers",
    )
