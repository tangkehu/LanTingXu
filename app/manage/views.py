
from flask import render_template

from . import manage_bp


@manage_bp.route('/user')
def user():
    return render_template('manage/user.html')
