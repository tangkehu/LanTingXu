
from flask import render_template
from . import sales_bp


@sales_bp.route('/day')
def day():
    return render_template('sales/day.html')
