from json_log_formatter import JSONFormatter


class CustomJsonFormatter(JSONFormatter):
    def json_record(self, message, extra, record):
        extra["logger_name"] = record.name

        if "context" in extra:
            context = extra.pop("context")
            if hasattr(context, "request"):
                extra = extra | {
                    "view": context.request.resolver_match.view_name,
                    "kwargs": context.request.resolver_match.kwargs,
                    "method": context.request.method,
                    "user_id": context.request.user.id if context.request.user.is_authenticated else None,
                    "session_key": context.request.session.session_key,
                }

        return super().json_record(message, extra, record)
