from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from wtforms import ValidationError

from app.models import GoodsType, Goods


class GoodsForm(FlaskForm):
    name = StringField('商品名', validators=[DataRequired('请输入商品名'), Length(1, 64, '商品名不超过64个字符')])
    type = SelectField('类别', validators=[DataRequired('请选择类别')], coerce=int)
    number = StringField('编号', validators=[Length(-1, 16, '编号不超过16个字符')])
    price = IntegerField('价格', validators=[DataRequired('请输入商品价格')])
    cash_pledge = IntegerField('押金', validators=[Optional()])
    size = StringField('尺码', validators=[Length(-1, 64, '尺码内容不超过64个字符')])
    brand = StringField('品牌', validators=[Length(-1, 64, '品牌名不超过64个字符')])
    quantity = IntegerField('库存', validators=[Optional()])
    details = TextAreaField('详情', validators=[Length(-1, 500, '详情描述不超过500个字符')])

    def __init__(self, *args, **kwargs):
        super(GoodsForm, self).__init__(*args, **kwargs)
        self.type.choices = [(-1, '请选择类别...')]+[(one.id, one.name) for one in GoodsType.query.all()]
        self.goods_obj_id = None

    def validate_type(self, field):
        if field.data == -1:
            raise ValidationError('请选择类别')

    def validate_number(self, field):
        if field.data and Goods.query.filter(Goods.id != self.goods_obj_id, Goods.number == field.data).first():
            raise ValidationError('该编号已被使用，请重新编号')

    def set_data(self, goods_obj):
        self.number.data = goods_obj.number
        self.name.data = goods_obj.name
        self.type.data = goods_obj.type_id or -1
        self.price.data = goods_obj.price
        self.cash_pledge.data = goods_obj.cash_pledge
        self.size.data = goods_obj.size
        self.brand.data = goods_obj.brand
        self.quantity.data = goods_obj.quantity
        self.details.data = goods_obj.details
