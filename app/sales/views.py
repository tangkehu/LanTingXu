
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, jsonify
from sqlalchemy import cast, DATE, extract
from flask_login import login_required

from . import sales_bp
from .forms import SalesOrderForm
from .. import db
from ..models import Goods, SalesOrder, GoodsType, GoodsImg
from ..utils import permission_required


@sales_bp.route('/')
@sales_bp.route('/<the_type>')
@sales_bp.route('/<the_type>/<the_date>')
@login_required
def index(the_type='day', the_date=None):
    # 这里有sqlalchemy关于日期查询的典型示例
    if the_type == 'day':
        the_date = datetime.strptime(the_date, '%Y-%m-%d') if the_date else datetime.now()
        order_find = SalesOrder.query.filter(
            cast(SalesOrder.create_time, DATE) == the_date.date(), SalesOrder.status != 0)
        current_date = the_date.strftime('%Y-%m-%d')
        current_type = 'day'  # 控制请求的url
        current_fmt = 'yyyy-mm-dd'  # 控制date插件显示的日期格式
        current_min_view = 0  # 控制date插件显示的粒度
        toggle_type = 'month'  # 控制切换
    else:
        the_date = datetime.strptime(the_date, '%Y-%m') if the_date else datetime.now()
        order_find = SalesOrder.query.filter(
            extract('year', SalesOrder.create_time) == the_date.year,
            extract('month', SalesOrder.create_time) == the_date.month,
            SalesOrder.status != 0)
        current_date = the_date.strftime('%Y-%m')
        current_type = 'month'
        current_fmt = 'yyyy-mm'
        current_min_view = 1
        toggle_type = 'day'
    order_list = order_find.order_by(SalesOrder.create_time.desc()).all()
    return render_template('sales/index.html', order_list=order_list, current_fmt=current_fmt, toggle_type=toggle_type,
                           current_min_view=current_min_view, current_date=current_date, current_type=current_type)


@sales_bp.route('/order_stat_api/<the_type>/<the_date>')
@login_required
def order_stat_api(the_type, the_date):
    # 在每次GET请求时清理无效订单
    SalesOrder.clear_invalid()
    return jsonify(SalesOrder.stat_data(the_type, the_date))


@sales_bp.route('/order_add_goods')
@sales_bp.route('/order_add_goods/<int:order_id>', methods=['GET', 'POST'])
@permission_required('order_manage')
def order_add_goods(order_id=None):
    if order_id is None:
        return redirect(url_for('.order_add_goods', order_id=SalesOrder().salesman_add()))
    else:
        current_order = SalesOrder.query.get_or_404(order_id)

    if request.method == 'POST':
        # 接收ajax发送的post请求，处理商品的追加和移除
        goods_id = request.form.get('goods_id')
        shift_type = request.form.get('shift_type')
        if shift_type == "append":
            current_order.salesman_goods_append(int(goods_id))
        else:
            current_order.salesman_goods_remove(int(goods_id))
        return "successful"

    goods_list = current_order.goods
    return render_template('sales/order_add_goods.html', goods_list=goods_list, order_id=order_id)


@sales_bp.route('/goods_search/<int:order_id>', methods=['GET', 'POST'])
@sales_bp.route('/goods_search/<int:order_id>/<int:type_id>', methods=['GET', 'POST'])
@login_required
def goods_search(order_id, type_id=None):
    type_id = type_id if type_id else GoodsType.query.first().id
    current_type = GoodsType.query.get_or_404(type_id).name
    goods_list = Goods.query.filter_by(type_id=type_id).order_by(Goods.create_time.desc()).all()
    type_list = GoodsType.query.all()

    if request.method == "POST":
        search_word = request.form.get('search_word', '').strip()
        if not search_word:
            return jsonify([])  # 搜索词无效则返回空

        goods_query = db.session.query(Goods.id, Goods.number, Goods.name,
                                       GoodsImg.filename_m, GoodsType.name, Goods.price).join(
            GoodsImg, GoodsImg.goods_id == Goods.id).join(GoodsType, GoodsType.id == Goods.type_id)

        goods_list = goods_query.filter(Goods.number == search_word).group_by(Goods.id).all()  # 默认查询编号
        if goods_list:
            pass
        elif search_word.isdigit():
            goods_list = goods_query.filter(Goods.id == int(search_word)).group_by(Goods.id).all()
        else:
            goods_list = goods_query.filter(Goods.name.like('%{}%'.format(search_word))).group_by(Goods.id).all()
        return jsonify(goods_list)

    return render_template('sales/search_goods.html', goods_list=goods_list, type_list=type_list,
                           current_type=current_type, order_id=order_id)


@sales_bp.route('/order_update/<int:order_id>', methods=['GET', 'POST'])
@permission_required('order_manage')
def order_update(order_id):
    current_order = SalesOrder.query.get_or_404(order_id)
    form = SalesOrderForm()

    if request.method == "GET":
        form.set_data(current_order)

    if form.validate_on_submit():
        current_order.salesman_update(form.total_real.data, form.pay_type.data, form.pay_status.data, form.remarks.data)
        flash('操作成功')
        return redirect(url_for('.index'))

    return render_template('sales/order_update.html', form=form)


@sales_bp.route('/order_info/<int:order_id>')
@login_required
def order_info(order_id):
    current_order = SalesOrder.query.get_or_404(order_id)
    return render_template('sales/order_info.html', current_order=current_order)


@sales_bp.route('/order_delete', methods=['POST'])
@permission_required('order_manage')
def order_delete():
    SalesOrder.query.get_or_404(int(request.form.get('order_id'))).salesman_close()
    return 'successful'
