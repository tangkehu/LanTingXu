from flask import render_template, redirect, url_for

from . import goods_bp


@goods_bp.route('/')
def index():
    return render_template('goods/index.html')


@goods_bp.route('/update_goods', methods=['GET', 'POST'])
def update_goods():
    return render_template('goods/update.html')


@goods_bp.route('/delete_goods')
def delete_goods():
    return redirect(url_for('.index'))
