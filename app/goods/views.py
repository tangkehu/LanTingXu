from flask import render_template

from . import goods_bp


@goods_bp.route('/')
def index():
    return render_template('goods/index.html')

