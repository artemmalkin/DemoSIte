from typing import Optional, Any

from flask import request
from flask_login import login_required

from blueprints.api import api
from blueprints.api.request import Request


@api.route('/<section>.<method>')
@login_required
def api(section: str, method: str) -> Optional[dict[str, Any]]:
    return Request(section, method, request.args).get_response()
