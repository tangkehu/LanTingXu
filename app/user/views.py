
from flask import render_template

from app.models import User
from . import user_bp


@user_bp.route('/<int:uid>')
@user_bp.route('/<int:uid>/<int:tid>')
def index(uid, tid=None):
    user_obj = User.query.get_or_404(uid)
    return render_template('user/base.html', user_obj=user_obj, type_id=tid)
