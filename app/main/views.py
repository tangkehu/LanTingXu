import os
from flask import render_template, url_for, request, send_file, current_app, flash, redirect, jsonify
from sqlalchemy import or_
from flask_login import current_user, login_required

from . import main_bp
from app.models import Goods, GoodsType, PvCount, User, WordCloud
from app.utils import goods_order_map, resize_img, random_filename
from app.manage.forms import UserForm


@main_bp.route('/')
@main_bp.route('/index')
def index():
    PvCount.add_home_count()
    data_carousel = Goods.search_for_carousel()
    data_user = User.query_for_homepage()
    data_recommend = Goods.query.filter(Goods.status == True).order_by(Goods.view_count.asc()).limit(6).all()
    data_hot_word = WordCloud.query_for_max_on_window(90, 1)
    return render_template('main/index.html', data_carousel=data_carousel, data_user=data_user,
                           data_hot_word=data_hot_word, data_recommend=data_recommend)


@main_bp.route('/all_goods')
@main_bp.route('/all_goods/<int:tid>/<string:order>')
def all_goods(tid=None, order='flow'):
    """ 所有商品分类展示 """
    tid = tid if tid else GoodsType.query.order_by(GoodsType.sequence.asc()).first().id
    data_goods = Goods.query.filter(Goods.status == True, Goods.type_id == tid).\
        order_by(goods_order_map(order, 0)).all()
    return render_template('main/all_goods.html', data_goods=data_goods, tid=tid, order=order,
                           type_li=GoodsType.query.order_by(GoodsType.sequence.asc()).all(),
                           goods_order_map=goods_order_map)


@main_bp.route('/usr_center')
def usr_center():
    name_dic = {'flow': '我的最受欢迎', 'date_down': '我的最新发布'}
    goods_data = [{
        'name': name_dic[key],
        'data': current_user.goods.filter(Goods.status==True).order_by(goods_order_map(key, 0)).limit(10).all(),
    } for key in name_dic if current_user.is_authenticated]
    goods_stat = current_user.get_goods_stat()
    return render_template('main/usr_center.html', goods_data=goods_data, goods_stat=goods_stat)


@main_bp.route('/usr_qrcode/<int:uid>')
def usr_qrcode(uid):
    return render_template('main/usr_qrcode.html', uid=uid)


@main_bp.route('/usr_account', methods=['GET', 'POST'])
@login_required
def usr_account():
    user_obj = current_user._get_current_object()
    form = UserForm(user_obj)

    if request.method == 'GET':
        form.set_data()

    if form.validate_on_submit():
        user_obj.edit(**form.data)
        flash('账号信息修改成功！')
        return redirect(url_for('.usr_account'))

    return render_template('main/usr_account.html', form=form)


@main_bp.route('/usr_home/<int:uid>')
@main_bp.route('/usr_home/<int:uid>/<int:tid>/<string:order>')
def usr_home(uid, tid=None, order='flow'):
    """ 用户个人主页 """
    PvCount.add_home_count()
    tid = tid if tid else GoodsType.query.order_by(GoodsType.sequence.asc()).first().id
    user_obj = User.query.get_or_404(uid)
    data_goods = user_obj.goods.filter(Goods.status == True, Goods.type_id == tid).\
        order_by(goods_order_map(order, 0)).all()
    return render_template('main/usr_home.html', user_obj=user_obj, goods=data_goods, uid=uid, tid=tid, order=order,
                           type_li=GoodsType.query.order_by(GoodsType.sequence.asc()).all(),
                           goods_order_map=goods_order_map)


@main_bp.route('/usr_bg_change_api', methods=['POST'])
@login_required
def usr_bg_change_api():
    # 背景图上传
    new_image = request.files.get('file')
    new_image_name = resize_img(current_app.config['BG_IMG_PATH'], random_filename(new_image.filename),
                                1080, new_image, True)
    current_user.change_bg_image(new_image_name)
    return 'success'


@main_bp.route('/goods_show/<int:goods_id>')
def goods_show(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    goods.add_view_count()
    return render_template('main/goods_show.html', goods=goods)


@main_bp.route('/search')
def search():
    """
    word: 搜索关键词
    order: 排序方式
    """
    word = request.args.get('word', '')
    order_way = request.args.get('order') if request.args.get('order') else 'flow'
    params = [Goods.status == True]
    if word:
        WordCloud.upsert(word)
        params.append(or_(Goods.name.like('%{}%'.format(word)), Goods.number.like('%{}%'.format(word))))
    else:
        params.append(Goods.id == 0)
    goods = Goods.query.filter(*params).order_by(goods_order_map(order_way, 0)).all()
    word_cloud = WordCloud.query_for_max_on_window(90)
    return render_template('main/search.html', goods=goods, word=word, order_way=order_way, word_cloud=word_cloud,
                           goods_order_map=goods_order_map)


@main_bp.route('/robots.txt')
def robots():
    return send_file(os.path.join(os.getcwd(), 'robots.txt'))


@main_bp.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(os.getcwd(), 'favicon.ico'))


# @main_bp.route('/')
# @main_bp.route('/<int:goods_id>')
# @main_bp.route('/index')
# @main_bp.route('/index/<int:goods_id>')
# def resist_regulation(goods_id=None):
#     """ 该路由在网站备案时开启，并将真实主页关闭 """
#     if goods_id:
#         goods = Goods.query.get_or_404(goods_id)
#         return jsonify({'name': goods.name,
#                         'cash_pledge': goods.cash_pledge,
#                         'size': goods.size,
#                         'quantity': goods.quantity,
#                         'images': [item.filename_l for item in goods.img.all()]})
#     goods_li = Goods.query.order_by(Goods.create_time.desc()).all()
#     return render_template('main/resist_regulation.html', goods_list=goods_li)
