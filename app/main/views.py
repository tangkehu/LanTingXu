import os
from flask import render_template, url_for, request, redirect, send_file

from . import main_bp
from app.models import Goods, GoodsType, HomePage, PvCount
from app.utils import goods_order_map


@main_bp.route('/')
@main_bp.route('/index')
def index():
    """
    tid: 商品类型
    order: 排序方式
    view: 展示方式
    """
    PvCount.add_home_count()
    body = HomePage.query.first()
    args = request.args.to_dict()
    tid = int(args.get('tid', GoodsType.query.order_by(GoodsType.sequence.asc()).first().id))
    order_way = args.get('order', 'flow')
    view_type = {'big': 'small', 'small': 'big'}[args.get('view', 'big')]
    params = [Goods.status == True, Goods.type_id == tid]
    goods_li = Goods.query.filter(*params).order_by(goods_order_map(order_way, 0)).all()
    return render_template('main/index.html', body=body, type_id=tid, order_way=order_way, view_type=view_type,
                           goods_li=goods_li)


@main_bp.route('/goods_show/<int:goods_id>')
def goods_show(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    goods.add_view_count()
    return render_template('main/goods_show.html', goods=goods)


@main_bp.route('/index_new')
def index_new():
    return redirect(url_for('.index'))


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
