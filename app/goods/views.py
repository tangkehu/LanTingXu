import os
from flask import render_template, redirect, url_for, request, current_app

from . import goods_bp


@goods_bp.route('/')
def index():
    goods_list = os.listdir(current_app.config['GOODS_IMG_PATH'])
    return render_template('goods/index.html', goods_list=goods_list)


@goods_bp.route('/update_goods', methods=['GET', 'POST'])
@goods_bp.route('/update_goods/<int:goods_id>', methods=['GET', 'POST'])
def update_goods(goods_id=None):
    """ 处理商品的添加和修改 """
    return render_template('goods/update.html', goods_id=goods_id)


@goods_bp.route('/img_goods', methods=['POST'])
def img_goods():
    img_up = request.files.get('file')
    if img_up:
        img_up.save(os.path.join(current_app.config['GOODS_IMG_PATH'], img_up.filename))
    return ''


@goods_bp.route('/delete_goods')
def delete_goods():
    return redirect(url_for('.index'))
