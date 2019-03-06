
from flask import render_template
from . import sales_bp


@sales_bp.route('/day')
def day():
    return render_template('sales/day.html')


@sales_bp.route('/order_update', methods=['GET', 'POST'])
def order_update():
    return render_template('sales/order_update.html')
