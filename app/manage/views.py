
from . import manage_bp


@manage_bp.route('/user')
def user():
    return 'ok'
