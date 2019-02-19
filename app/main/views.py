from flask import render_template, jsonify

from . import main_bp
from app.models import Goods, GoodsType


@main_bp.route('/')
@main_bp.route('/<int:type_id>')
def index(type_id=None):
    type_list = GoodsType.query.all()
    if type_id:
        goods_list = Goods.query.filter_by(type_id=type_id).order_by(Goods.create_time.desc()).all()
        current_type = GoodsType.query.get_or_404(type_id).name
    else:
        goods_list = Goods.query.order_by(Goods.create_time.desc()).all()
        current_type = '全部类别'
    return render_template('main/index.html', goods_list=goods_list, type_list=type_list, current_type=current_type)


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
