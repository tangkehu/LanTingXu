import os
from flask import render_template, url_for, request, redirect, send_file
from sqlalchemy import or_
from flask_login import current_user

from . import main_bp
from app.models import Goods, GoodsType, PvCount
from app.utils import goods_order_map


@main_bp.route('/')
@main_bp.route('/index')
def index():
    PvCount.add_home_count()
    name_dic = {'date_down': '最新发布', 'flow': '最多浏览', 'price_up': '平价优选', 'price_down': '汉服精品'}
    goods_data = [{
        'name': name_dic[key],
        'data': Goods.query.filter_by(status=True).order_by(goods_order_map(key, 0)).limit(6).all(),
        'href': url_for('.show_in_order', order=key)
    } for key in name_dic]
    return render_template('main/index.html', goods_data=goods_data, type_li=GoodsType.query.all())


@main_bp.route('/show_in_order/<string:order>')
def show_in_order(order):
    name_dic = {'date_down': '最新发布', 'flow': '最多浏览', 'price_up': '平价优选', 'price_down': '汉服精品'}
    name = name_dic[order]
    goods_data = Goods.query.filter_by(status=True).order_by(goods_order_map(order, 0)).all()
    return render_template('main/show_in_order.html', name=name, goods_data=goods_data)


@main_bp.route('/show_in_type/<int:tid>')
def show_in_type(tid):
    """ args:: order: 商品排序方式; view: 商品展现方式 """
    name = GoodsType.query.get_or_404(tid).name
    args = request.args.to_dict()
    order = args.get('order') if args.get('order') else 'flow'
    view = args.get('view') if args.get('view') else 'big'
    goods_data = Goods.query.filter_by(status=True, type_id=tid).order_by(goods_order_map(order, 0)).all()
    return render_template('main/show_in_type.html', name=name, goods_data=goods_data, tid=tid, order=order, view=view)


@main_bp.route('/usr_center')
def usr_center():
    name_dic = {'flow': '我的最受欢迎', 'date_down': '我的最新发布'}
    goods_data = [{
        'name': name_dic[key],
        'data': current_user.goods.filter(Goods.status==True).order_by(goods_order_map(key, 0)).limit(10).all(),
    } for key in name_dic if current_user.is_authenticated]
    goods_stat = current_user.get_goods_stat()
    return render_template('main/usr_center.html', goods_data=goods_data, goods_stat=goods_stat)


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
        params.append(or_(Goods.name.like('%{}%'.format(word)), Goods.number.like('%{}%'.format(word))))
    else:
        params.append(Goods.id == 0)
    goods = Goods.query.filter(*params).order_by(goods_order_map(order_way, 0)).all()
    return render_template('main/search.html', goods=goods, word=word, order_way=order_way)


@main_bp.route('/robots.txt')
def robots():
    return send_file(os.path.join(os.getcwd(), 'robots.txt'))


@main_bp.route('/favicon.ico')
def favicon():
    return send_file(os.path.join(os.getcwd(), 'favicon.ico'))


# @main_bp.route('/index_new')
# @main_bp.route('/index_new/<int:type_id>')
# def index_new(type_id=None):
#     """ 备用首页 """
#     PvCount.add_home_count()
#     body = HomePage.query.first()
#     type_id = type_id if type_id else GoodsType.query.filter_by(sequence=1).first().id
#     type_list = GoodsType.query.all()
#     return render_template('main/index.html', body=body, type_id=type_id, type_list=type_list)


# 分页展示部分代码——备用
# @main_bp.route('/goods_list/<int:tid>/<int:page>')
# def goods_list(tid=0, page=1):
#     # 获取商品分页展示数据
#     filters = [Goods.type_id == tid, Goods.status == True] if tid is not 0 else [Goods.status == True]
#     pagination = db.session.query(Goods.id, Goods.name, GoodsImg.filename_m, Goods.number).join(
#         GoodsImg, GoodsImg.goods_id == Goods.id).filter(*filters).group_by(Goods.id).order_by(
#         Goods.price.asc()).paginate(page, current_app.config['PER_PAGE'], False)
#     return jsonify({'items': [render_template('main/masonry_item.html', item=item) for item in pagination.items],
#                     'next': url_for('.goods_list', tid=tid, page=pagination.next_num) if pagination.next_num else None})


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
