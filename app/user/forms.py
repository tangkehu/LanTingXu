from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class GoodsForm(FlaskForm):
    name = StringField('商品名', validators=[DataRequired('请输入商品名'), Length(1, 64, '商品名不超过64个字符')])
    rent = IntegerField('租金', validators=[DataRequired('请输入租金')])
    cash_pledge = IntegerField('押金', validators=[Optional()])
    size = StringField('尺码', validators=[Length(-1, 64, '尺码内容不超过64个字符')])
    brand = StringField('品牌', validators=[Length(-1, 64, '品牌名不超过64个字符')])
    quantity = IntegerField('库存', validators=[Optional()])
    details = TextAreaField('详情', validators=[Length(-1, 500, '详情描述不超过500个字符')])

    def set_data(self, goods_obj):
        self.name.data = goods_obj.name
        self.rent.data = goods_obj.rent
        self.cash_pledge.data = goods_obj.cash_pledge
        self.size.data = goods_obj.size
        self.brand.data = goods_obj.brand
        self.quantity.data = goods_obj.quantity
        self.details.data = goods_obj.details
