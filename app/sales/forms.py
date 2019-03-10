
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, TextAreaField, RadioField
from wtforms.validators import DataRequired


class SalesOrderForm(FlaskForm):
    order_number = StringField(label="订单编号")
    price = FloatField(label="商品总价")
    pledge = FloatField(label="商品押金")
    order_total = FloatField(label="订单合计")
    pay_type = SelectField(label="付款方式", choices=[('现金', '现金'), ('微信', '微信'), ('支付宝', '支付宝'), ('其它', '其它')])
    pay_status = RadioField("付款状态", coerce=int, choices=[(1, "已付款"), (0, "未付款")])
    remarks = TextAreaField("备注")
    total_real = FloatField("实付款", validators=[DataRequired(message='请输入实付款额')])

    def set_data(self, order_obj):
        self.order_number.data = '{:0>5}'.format(order_obj.id)
        self.price.data = order_obj.price
        self.pledge.data = order_obj.pledge
        self.order_total.data = order_obj.price+order_obj.pledge
        self.pay_type.data = order_obj.pay_type if order_obj.pay_type else "支付宝"
        self.pay_status.data = 1 if order_obj.pay_status else 0
        self.remarks.data = order_obj.remarks
        self.total_real.data = order_obj.total_real
