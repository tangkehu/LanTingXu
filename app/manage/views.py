
from flask import render_template, request, jsonify

from app.models import User, Role, Permission
from . import manage_bp


@manage_bp.route('/user', methods=['GET', 'POST'])
def user():
    """ 用户查看，用户密码修改 """
    if request.method == 'POST':
        User.query.get_or_404(int(request.form.get('user_id', 0))).change_password(request.form.get('password'))
        return 'successful'

    users = User.query.order_by(User.id.desc()).all()
    return render_template('manage/user.html', users=users)


@manage_bp.route('/user_delete', methods=['POST'])
def user_delete():
    User.query.get_or_404(int(request.form.get('user_id', 0))).delete()
    return 'successful'


@manage_bp.route('/user_role/<user_id>', methods=['GET', 'POST'])
def user_role(user_id):
    the_user = User.query.get_or_404(int(user_id))

    if request.method == "POST":
        role_id = request.form.get('role_id')
        status = request.form.get('status')
        if status == 'append':
            the_user.append_role(int(role_id))
        else:
            the_user.remove_role(int(role_id))
        return 'successful'

    return jsonify([(item.name, item.id) for item in Role.query.all()
                    if the_user.roles.filter(Role.id == item.id).count() is 0])


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


@manage_bp.route('/role_delete', methods=['POST'])
def role_delete():
    Role.query.get_or_404(int(request.form.get('role_id', 0))).delete()
    return 'successful'


@manage_bp.route('/permission/<role_id>', methods=['GET', 'POST'])
def permission(role_id):
    """ 角色权限的添加和移除 """
    result = []
    the_role = Role.query.get_or_404(int(role_id))

    if request.method == "POST":
        permission_id = request.form.get('permission_id')
        status = request.form.get('status')
        if status == 'true':
            the_role.append_permission(permission_id)
        else:
            the_role.remove_permission(permission_id)
        return 'successful'

    for item in Permission.query.all():
        if the_role.permissions.filter(Permission.name == item.name).count() > 0:
            result.append((item.name, item.id, 1))
        else:
            result.append((item.name, item.id, 0))
    return jsonify(result)
