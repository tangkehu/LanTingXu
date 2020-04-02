from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user

from . import goods_bp
from .forms import GoodsForm
from app.models import GoodsImg, Goods, GoodsType
from app.utils import permission_required, goods_order_map


@goods_bp.route('/')
@login_required
def index():
    """
    tid: 当其为0时表示类型为已下架商品
    order: 表示排序方式
    """
    args = request.args.to_dict()
    type_id = int(args.get('tid', GoodsType.query.order_by(GoodsType.sequence.asc()).first().id))
    order_way = args.get('order', 'date_down')
    params = [Goods.type_id == type_id, Goods.status == True] if type_id else [Goods.status == False]
    if not current_user.can('system_manage'):
        params.append(Goods.user_id == current_user.id)
    goods_list = Goods.query.filter(*params).order_by(goods_order_map(order_way, 0)).all()
    return render_template('goods/index.html', goods_list=goods_list, type_id=type_id, order_way=order_way,
                           goods_order_map=goods_order_map, type_li=GoodsType.query.all())


@goods_bp.route('/update_goods/<int:type_id>', methods=['GET', 'POST'])
@goods_bp.route('/update_goods/<int:type_id>/<int:goods_id>', methods=['GET', 'POST'])
@permission_required('goods_manage')
@login_required
def update_goods(type_id, goods_id=None):
    """ 处理商品的添加和修改
     :param type_id: 用于定位返回页面的位置
     :param goods_id: 商品ID
     """
    form = GoodsForm()
    goods = Goods.query.get_or_404(goods_id) if goods_id else None
    form.goods_obj_id = goods.id if goods else None

    if request.method == 'GET':
        if type_id > 0:
            form.type.data = type_id
        for item in GoodsImg.query.filter_by(status=False, user_id=current_user.id).all():
            # 清理未关联的商品图
            item.delete()
        if goods is not None:
            # 商品编辑时的表单内容注入
            form.set_data(goods)

    if form.validate_on_submit():
        kwargs = {'number': form.number.data, 'type': form.type.data, 'cash_pledge': form.cash_pledge.data,
                  'size': form.size.data, 'brand': form.brand.data, 'quantity': form.quantity.data,
                  'details': form.details.data}
        if goods is None:
            if GoodsImg.query.filter_by(status=False, user_id=current_user.id).first():
                Goods().add(form.name.data, form.price.data, **kwargs)
                flash('商品添加成功。')
                return redirect(url_for('.index', type_id=form.type.data))
            else:
                flash('请添加商品图。')
        else:
            goods.edit(form.name.data, form.price.data, **kwargs)
            flash('商品修改成功。')
            return redirect(url_for('.index', type_id=type_id)+'#goods_{}'.format(goods_id))

    return render_template('goods/update_goods.html', form=form, goods=goods)


@goods_bp.route('/delete_goods', methods=['POST'])
@permission_required('goods_manage')
@login_required
def delete_goods():
    Goods.query.get_or_404(int(request.form.get('goods_id'))).delete()
    return 'successful'


@goods_bp.route('/alt_status', methods=['POST'])
@permission_required('goods_manage')
@login_required
def alt_status():
    Goods.query.get_or_404(int(request.form.get('goods_id'))).update_status()
    return 'successful'


@goods_bp.route('/img_goods_show')
@goods_bp.route('/img_goods_show/<int:goods_id>')
@permission_required('goods_manage')
@login_required
def img_goods_show(goods_id=None):
    records = []
    if goods_id is not None:
        for item in GoodsImg.query.filter_by(goods_id=goods_id).all():
            records.append((item.id, item.filename_s))
    else:
        for item in GoodsImg.query.filter_by(status=False, user_id=current_user.id).all():
            records.append((item.id, item.filename_s))
    return jsonify(records)


@goods_bp.route('/img_goods_upload', methods=['POST'])
@goods_bp.route('/img_goods_upload/<int:goods_id>', methods=['POST'])
@permission_required('goods_manage')
@login_required
def img_goods_upload(goods_id=None):
    # for item in request.files.getlist('file'):  # 处理多文件上传的典型案例，纪念一下
    result = GoodsImg().add(request.files.get('file'), goods_id=goods_id)
    if result['status'] is True:
        return jsonify(result['img_obj'].id)
    else:
        return 'error', 400


@goods_bp.route('/img_goods_delete', methods=["POST"])
@permission_required('goods_manage')
@login_required
def img_goods_delete():
    GoodsImg.query.get_or_404(int(request.form.get('img_id'))).delete()
    return 'successful'

