from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class GoodsForm(FlaskForm):
    name = StringField('商品名', validators=[DataRequired('请输入商品名'), Length(1, 64, '商品名不超过64个字符')])
    rent = IntegerField('租金', validators=[DataRequired('请输入租金')])
    cash_pledge = IntegerField('押金', validators=[Optional()])
    brand = StringField('品牌', validators=[Length(-1, 64, '品牌名不超过64个字符')])
    details = TextAreaField('详情', validators=[Length(-1, 500, '详情描述不超过500个字符')])

    def set_data(self, goods_obj):
        self.name.data = goods_obj.name
        self.rent.data = goods_obj.rent
        self.cash_pledge.data = goods_obj.cash_pledge
        self.brand.data = goods_obj.brand
        self.details.data = goods_obj.details


class GoodsDeleteForm(FlaskForm):
    goods_id = IntegerField(validators=[DataRequired('未找到要删除的对象。')])
