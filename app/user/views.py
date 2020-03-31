
from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user, login_required

from app.models import User, Goods, PvCount
from app.manage.forms import UserForm
from app.utils import goods_order_map as _order
from app.utils import resize_img, random_filename
from . import user_bp


@user_bp.route('/<int:uid>')
def index(uid):
    """
    tid: 商品类型，当其为0时表示首页
    order: 排序方式
    view: 展示方式
    """
    PvCount.add_home_count()
    user_obj = User.query.get_or_404(uid)
    args = request.args.to_dict()
    tid = int(args.get('tid', 0))
    order_way = args.get('order', 'flow')
    view_type = {'big': 'small', 'small': 'big'}[args.get('view', 'big')]

    params = [Goods.status == True, ]
    if tid:
        params.append(Goods.type_id == tid)
    goods_li = user_obj.goods.filter(*params).order_by(_order(order_way, 0)).all()
    return render_template('user/index.html', user_obj=user_obj, type_id=tid, order_way=order_way, view_type=view_type,
                           goods_li=goods_li)


@user_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_obj = current_user._get_current_object()
    form = UserForm(user_obj)

    if request.method == 'GET':
        form.set_data()

    if form.validate_on_submit():
        user_obj.edit(**form.data)
        flash('账号信息修改成功！')
        return redirect(url_for('.account'))

    return render_template('user/account.html', form=form)


@user_bp.route('/bg_change', methods=['POST'])
@login_required
def bg_change():
    # 背景图上传
    new_image = request.files.get('file')
    new_image_name = resize_img(current_app.config['BG_IMG_PATH'], random_filename(new_image.filename),
                                1080, new_image, True)
    user_obj = current_user._get_current_object()
    user_obj.change_bg_image(new_image_name)
    return 'success'
