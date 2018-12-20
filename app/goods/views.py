from flask import render_template, redirect, url_for, request
from flask_login import login_required

from . import goods_bp
from .forms import GoodsForm
from app.models import GoodsImg, Goods


@goods_bp.route('/')
def index():
    goods_list = Goods.query.all()
    return render_template('goods/index.html', goods_list=goods_list)


@goods_bp.route('/update_goods', methods=['GET', 'POST'])
@goods_bp.route('/update_goods/<int:goods_id>', methods=['GET', 'POST'])
@login_required
def update_goods(goods_id=None):
    """ 处理商品的添加和修改 """
    form = GoodsForm()
    goods = Goods.query.get_or_404(goods_id) if goods_id else None
    if form.validate_on_submit():
        if goods is None:
            Goods().add(form.name.data, form.rent.data)
        else:
            goods.edit(form.name.data, form.rent.data)
        return redirect(url_for('.index'))
    if goods is not None and request.method == 'GET':
        form.set_data(goods.name, goods.rent)
    return render_template('goods/update.html', form=form, goods=goods)


@goods_bp.route('/img_goods', methods=['POST'])
@login_required
def img_goods():
    img_up = request.files.get('file')
    if img_up:
        result = GoodsImg().add(img_up)
        if result['status'] is True:
            return result['msg'], 200
        else:
            return result['msg'], 400
    return ''


@goods_bp.route('/delete_goods')
@login_required
def delete_goods():
    return redirect(url_for('.index'))
