from flask import render_template, jsonify, current_app, url_for

from . import main_bp
from app import db
from app.models import Goods, GoodsType, GoodsImg


@main_bp.route('/')
@main_bp.route('/<int:type_id>')
def index(type_id=0):
    type_list = GoodsType.query.all()
    current_type = '全部类别' if type_id is 0 else GoodsType.query.get_or_404(type_id).name
    return render_template('main/test.html', type_id=type_id, type_list=type_list, current_type=current_type)


@main_bp.route('/goods_list/<int:tid>/<int:page>')
def goods_list(tid=0, page=1):
    # 获取商品分页展示数据
    filters = [Goods.type_id == tid] if tid is not 0 else []
    pagination = db.session.query(Goods.id, Goods.name, GoodsImg.filename_m).join(
        GoodsImg, GoodsImg.goods_id == Goods.id).filter(*filters).group_by(Goods.id).order_by(
        Goods.create_time.desc()).paginate(page, current_app.config['PER_PAGE'], False)
    return jsonify({'items': list(pagination.items),
                    'next': url_for('.goods_list', tid=tid, page=pagination.next_num) if pagination.next_num else None})


@main_bp.route('/goods_show/<int:goods_id>')
def goods_show(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    return render_template('main/goods_show.html', goods=goods)


@main_bp.route('/goods_no_price')
@main_bp.route('/goods_no_price/<int:goods_id>')
def goods_no_price(goods_id=None):
    if goods_id:
        goods = Goods.query.get_or_404(goods_id)
        return jsonify({'name': goods.name,
                        'cash_pledge': goods.cash_pledge,
                        'size': goods.size,
                        'quantity': goods.quantity,
                        'images': [item.filename_m for item in goods.img.all()]})
    goods_list = Goods.query.order_by(Goods.create_time.desc()).all()
    return render_template('main/goods_no_price.html', goods_list=goods_list)
