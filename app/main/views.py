from flask import render_template, jsonify, current_app, url_for, redirect

from . import main_bp
from app import db
from app.models import Goods, GoodsType, GoodsImg, HomePage


# @main_bp.route('/')
# @main_bp.route('/<int:type_id>')
# @main_bp.route('/index')
# @main_bp.route('/index/<int:type_id>')
# def index(type_id=None):
#     type_id = type_id if type_id else GoodsType.query.first().id
#     type_list = GoodsType.query.all()
#     body = HomePage.query.first()
#     current_type = GoodsType.query.get_or_404(type_id).name
#     return redirect(url_for('.index_new'))
#     return render_template('main/blank.html')
#     return render_template('main/index.html',
#                            type_id=type_id, type_list=type_list, current_type=current_type, body=body)


@main_bp.route('/goods_list/<int:tid>/<int:page>')
def goods_list(tid=0, page=1):
    # 获取商品分页展示数据
    filters = [Goods.type_id == tid, Goods.status == True] if tid is not 0 else [Goods.status == True]
    pagination = db.session.query(Goods.id, Goods.name, GoodsImg.filename_m, Goods.number).join(
        GoodsImg, GoodsImg.goods_id == Goods.id).filter(*filters).group_by(Goods.id).order_by(
        Goods.create_time.desc()).paginate(page, current_app.config['PER_PAGE'], False)
    return jsonify({'items': [render_template('main/masonry_item.html', item=item) for item in pagination.items],
                    'next': url_for('.goods_list', tid=tid, page=pagination.next_num) if pagination.next_num else None})


@main_bp.route('/goods_show/<int:goods_id>')
def goods_show(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    return render_template('main/goods_show.html', goods=goods)


@main_bp.route('/')
@main_bp.route('/<int:goods_id>')
@main_bp.route('/index')
@main_bp.route('/index/<int:goods_id>')
@main_bp.route('/goods_no_price')
@main_bp.route('/goods_no_price/<int:goods_id>')
def goods_no_price(goods_id=None):
    if goods_id:
        goods = Goods.query.get_or_404(goods_id)
        return jsonify({'name': goods.name,
                        'cash_pledge': goods.cash_pledge,
                        'size': goods.size,
                        'quantity': goods.quantity,
                        'images': [item.filename_l for item in goods.img.all()]})
    goods_li = Goods.query.order_by(Goods.create_time.desc()).all()
    return render_template('main/goods_no_price.html', goods_list=goods_li)


@main_bp.route('/index_new')
@main_bp.route('/index_new/<int:type_id>')
def index_new(type_id=None):
    body = HomePage.query.first()
    type_id = type_id if type_id else GoodsType.query.filter_by(sequence=1).first().id
    type_list = GoodsType.query.all()
    return render_template('main/index_new.html', body=body, type_id=type_id, type_list=type_list)
