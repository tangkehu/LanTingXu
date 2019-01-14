from flask import render_template, jsonify

from . import main_bp
from app.models import Goods


@main_bp.route('/')
def index():
    goods_list = Goods.query.order_by(Goods.create_time.desc()).all()
    return render_template('main/index.html', goods_list=goods_list)


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
