
from flask import render_template, request

from app.models import User, Role
from . import manage_bp


@manage_bp.route('/user')
def user():
    users = User.query.all()
    return render_template('manage/user.html', users=users)


@manage_bp.route('/role', methods=['GET', 'POST'])
def role():
    """ 用户角色的查看、添加和修改。 """
    if request.method == 'POST':
        role_id = request.form.get('role_id', -1) or -1
        role_name = request.form.get('role_name', None)
        role_details = request.form.get('role_details', None)

        if not role_name or Role.query.filter(Role.name == role_name, Role.id != int(role_id)).count() > 0:
            return '角色名非空且唯一', 400

        if role_id is not -1:
            Role.query.get_or_404(int(role_id)).add(role_name, role_details)
        else:
            Role().add(role_name, role_details)
        return 'successful'

    roles = Role.query.order_by(Role.id.desc()).all()
    return render_template('manage/role.html', roles=roles)
