from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user

from . import goods_bp
from .forms import GoodsForm, UserForm
from app.models import GoodsImg, Goods, GoodsType
from app.utils import permission_required


@goods_bp.route('/')
@goods_bp.route('/<int:type_id>')
@login_required
def index(type_id=None):
    if type_id:
        current_type = GoodsType.query.get_or_404(type_id).name
        goods_list = Goods.query.filter_by(type_id=type_id).order_by(Goods.updata_time.desc()).all()
    else:
        current_type = "全部类别"
        goods_list = Goods.query.order_by(Goods.updata_time.desc()).all()
    type_list = GoodsType.query.all()
    return render_template('goods/index.html', goods_list=goods_list, type_list=type_list, current_type=current_type)


@goods_bp.route('/update_goods', methods=['GET', 'POST'])
@goods_bp.route('/update_goods/<int:goods_id>', methods=['GET', 'POST'])
@permission_required('sell')
@login_required
def update_goods(goods_id=None):
    """ 处理商品的添加和修改 """
    form = GoodsForm()
    goods = Goods.query.get_or_404(goods_id) if goods_id else None

    if request.method == 'GET':
        for item in GoodsImg.query.filter_by(status=False, user_id=current_user.id).all():
            # 清理未关联的商品图
            item.delete()
        if goods is not None:
            # 商品编辑时的表单内容注入
            form.set_data(goods)

    if form.validate_on_submit():
        kwargs = {'type': form.type.data, 'cash_pledge': form.cash_pledge.data, 'size': form.size.data,
                  'brand': form.brand.data, 'quantity': form.quantity.data, 'details': form.details.data}
        if goods is None:
            if GoodsImg.query.filter_by(status=False, user_id=current_user.id).first():
                Goods().add(form.name.data, form.rent.data, **kwargs)
                flash('商品添加成功。')
                return redirect(url_for('.index'))
            else:
                flash('请添加商品图。')
        else:
            goods.edit(form.name.data, form.rent.data, **kwargs)
            flash('商品修改成功。')
            return redirect(url_for('.index')+'#goods_{}'.format(goods_id))

    return render_template('goods/update_goods.html', form=form, goods=goods)


@goods_bp.route('/delete_goods', methods=['POST'])
@permission_required('sell')
@login_required
def delete_goods():
    Goods.query.get_or_404(int(request.form.get('goods_id'))).delete()
    return 'successful'


@goods_bp.route('/img_goods_show')
@goods_bp.route('/img_goods_show/<int:goods_id>')
@permission_required('sell')
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
@permission_required('sell')
@login_required
def img_goods_upload(goods_id=None):
    fail_msg = ''
    success_msg = ''
    img = []
    for item in request.files.getlist('file'):  # 处理多文件上传的典型案例
        result = GoodsImg().add(item, goods_id=goods_id)
        if result['status'] is True:
            success_msg = result['msg']
            img.append((result['img_obj'].id, result['img_obj'].filename_s))
        else:
            fail_msg = result['msg']
    result = {'msg': fail_msg if fail_msg else success_msg, 'img': img}
    return jsonify(result)


@goods_bp.route('/img_goods_delete', methods=["POST"])
@permission_required('sell')
@login_required
def img_goods_delete():
    GoodsImg.query.get_or_404(int(request.form.get('img_id'))).delete()
    return 'successful'


@goods_bp.route('/update_user', methods=['GET', 'POST'])
@login_required
def update_user():
    form = UserForm()
    if request.method == 'GET':
        form.set_data()
    if form.validate_on_submit():
        kwargs = {'username': form.username.data, 'email': form.email.data, 'password': form.password.data,
                  'phone_number': form.phone_number.data, 'resume': form.resume.data}
        current_user.edit(**kwargs)
        flash('账户信息修改成功！')
        return redirect(url_for('.index'))
    return render_template('goods/update_user.html', form=form)