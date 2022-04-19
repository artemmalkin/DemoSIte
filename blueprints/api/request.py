from typing import Optional, Any

from werkzeug.datastructures import MultiDict

from blueprints.api.errors import Error
from blueprints.api.sections import Messages, Users, Chats, Notifications


class Request:
    def __init__(self, section: str = None, method: str = None, args: MultiDict[str, str] = None):
        # Define exists Section classes and give request.args to them from view function
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

    def get_method_list(self):
        # Output all methods for debug
        result = dict()
        for key in self.sections.keys():
            result[key] = []
            for method in self.sections[key].method:
                result[key].append(method)
        return result
