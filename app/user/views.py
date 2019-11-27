
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

from app.models import User, Goods
from app.manage.forms import UserForm
from . import user_bp


@user_bp.route('/<int:uid>')
def index(uid):
    """
    接受的http get 参数包括 tid,
    """
    user_obj = User.query.get_or_404(uid)
    args = request.args.to_dict()
    tid = int(args.get('tid', 0))

    if tid:
        goods_li = user_obj.goods.filter(Goods.status == True, Goods.type_id == tid).order_by(Goods.price.asc()).all()
    else:
        goods_li = user_obj.goods.filter(Goods.status == True).order_by(Goods.updata_time.desc()).all()
    return render_template('user/base.html', user_obj=user_obj, type_id=tid, goods_li=goods_li)


@user_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_obj = current_user._get_current_object()
    form = UserForm(user_obj)

    if request.method == 'GET':
        form.set_data()

    if form.validate_on_submit():
        kwargs = {'username': form.username.data, 'email': form.email.data, 'phone_number': form.phone_number.data,
                  'resume': form.resume.data, 'password': form.password.data}
        user_obj.edit(**kwargs)
        flash('账号信息修改成功！')
        return redirect(url_for('.account'))

    return render_template('user/account.html', form=form)
