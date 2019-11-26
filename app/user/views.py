
from flask import render_template, request

from app.models import User, Goods
from . import user_bp


@user_bp.route('/<int:uid>')
def index(uid):
    """
    接受的http get 参数包括 tid,
    """
    user_obj = User.query.get_or_404(uid)
    args = request.args.to_dict()
    tid = int(args.get('tid', 0))

    if tid:
        goods_li = user_obj.goods.filter(Goods.status == True, Goods.type_id == tid).order_by(Goods.price.asc()).all()
    else:
        goods_li = user_obj.goods.filter(Goods.status == True).order_by(Goods.updata_time.desc()).all()
    return render_template('user/base.html', user_obj=user_obj, type_id=tid, goods_li=goods_li)
