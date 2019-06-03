
from flask import request
from . import api_bp


@api_bp.route('/wx/msg')
def wx_msg():
    return request.args.get('echostr', '')

