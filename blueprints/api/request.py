from typing import Optional, Any

from werkzeug.datastructures import MultiDict

from blueprints.api.errors import Error
from blueprints.api.sections import Messages, Users, Chats, Notifications


class Request:
    def __init__(self, section: str, method: str, args: MultiDict[str, str]):
        self.sections = {
            "messages": Messages(args),
            "users": Users(args),
            "chats": Chats(args),
            "notifications": Notifications(args)
        }

        self.section = section
        self.method = method

    def get_response(self) -> Optional[dict[str, Any]]:
        section = self.sections.get(self.section)
        method = section.method.get(self.method) if section is not None else None

        if method is not None:
            return {f"{self.section}.{self.method}": method()}
        else:
            return {'error': Error.UnknownMethod}

# def handle_query_strings(api: object) -> Callable[[{__name__}], Callable[[], Any]]:
#     """
#     Put into the context's dict a response if having a query strings
#
#     :param api: class object of methods
#     :return: context
#     """
#
#     def get_response(func):
#         def wrapper():
#             if request.args:
#                 context = dict()
#
#                 act = request.args.get('act')
#                 acts = {
#                     'new': 'act-new-chat',
#                 }
#
#                 if act in acts:
#                     context.update(act=acts[act])
#
#                 response = Request(api, request.args).get_response()
#                 context.update(response=response)
#                 return func(context)
#             else:
#                 return func()
#
#         wrapper.__name__ = func.__name__
#         return wrapper
#
#     return get_response
