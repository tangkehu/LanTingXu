
from flask import render_template, redirect, url_for, request, flash
from . import sales_bp
from .forms import SalesOrderForm
from ..models import Goods, SalesOrder, RelationOrderGoods


@sales_bp.route('/day')
def day():
    # TODO: 后续按天查找
    # 在每次GET请求时清理无效订单
    SalesOrder.clear_invalid()
    order_list = SalesOrder.query.filter(SalesOrder.status != 0).order_by(SalesOrder.create_time.desc()).all()
    return render_template('sales/day.html', order_list=order_list)


@sales_bp.route('/order_add_goods')
@sales_bp.route('/order_add_goods/<int:order_id>', methods=['GET', 'POST'])
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
def goods_search(order_id):
    goods_list = []
    if request.method == "POST":
        search_word=request.form.get('search_word')
        if search_word.isdigit():
            goods_list = Goods.query.filter_by(id=int(search_word)).all()
        else:
            goods_list = Goods.query.filter(Goods.name.like('%{}%'.format(search_word))).all()
    return render_template('sales/search_goods.html', goods_list=goods_list, order_id=order_id)


@sales_bp.route('/order_update/<int:order_id>', methods=['GET', 'POST'])
def order_update(order_id):
    current_order = SalesOrder.query.get_or_404(order_id)
    form = SalesOrderForm()

    if request.method == "GET":
        form.set_data(current_order)

    if form.validate_on_submit():
        current_order.salesman_update(form.total_real.data, form.pay_type.data, form.pay_status.data, form.remarks.data)
        flash('新订单创建成功')
        return redirect(url_for('.day'))

    return render_template('sales/order_update.html', form=form)


@sales_bp.route('/order_info/<int:order_id>')
def order_info(order_id):
    goods_list = []
    return render_template('sales/order_info.html', goods_list=goods_list)