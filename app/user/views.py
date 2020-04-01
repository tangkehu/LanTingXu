
from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user, login_required

from app.models import User, Goods, PvCount, GoodsType
from app.manage.forms import UserForm
from app.utils import goods_order_map as _order
from app.utils import resize_img, random_filename
from . import user_bp


@user_bp.route('/<int:uid>')
def index(uid):
    """ 个人主页 """
    PvCount.add_home_count()
    user_obj = User.query.get_or_404(uid)
    name_dic = {'date_down': '最新发布', 'flow': '最多浏览', 'price_up': '平价优选', 'price_down': '精品推荐'}
    tid = GoodsType.query.order_by(GoodsType.sequence.asc()).first().id

    def set_data(order):
        return {
            'name': name_dic[order],
            'data': user_obj.goods.filter(Goods.status==True).order_by(_order(order, 0)).limit(5).all(),
            'href': url_for('.type_show', uid=uid, tid=tid)+'?order='+order
        }

    return render_template('user/index.html', user_obj=user_obj, goods_data=[set_data(key) for key in name_dic])


@user_bp.route('/<int:uid>/<int:tid>')
def type_show(uid, tid):
    """ 个人主页商品分类展示 args:: order: 排序方式; view: 展示方式; """
    user_obj = User.query.get_or_404(uid)
    args = request.args.to_dict()
    order_way = args.get('order') if args.get('order') else 'flow'
    view_type = args.get('view') if args.get('view') else 'big'
    params = [Goods.status == True, Goods.type_id == tid]
    goods_li = user_obj.goods.filter(*params).order_by(_order(order_way, 0)).all()
    return render_template('user/type_show.html', user_obj=user_obj, type_id=tid, order_way=order_way,
                           view_type=view_type, goods_li=goods_li)


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
