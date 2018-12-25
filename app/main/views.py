from flask import render_template

from . import main_bp
from app.models import Goods


@main_bp.route('/')
def index():
    goods_list = Goods.query.order_by(Goods.create_time.desc()).all()
    return render_template('main/index.html', goods_list=goods_list)


@main_bp.route('/show/<int:goods_id>')
def show(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    return render_template('main/show.html', goods=goods)
