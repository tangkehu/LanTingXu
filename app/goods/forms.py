from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp
from wtforms import ValidationError
from flask_login import current_user

from app.models import User, GoodsType


class GoodsForm(FlaskForm):
    name = StringField('商品名', validators=[DataRequired('请输入商品名'), Length(1, 64, '商品名不超过64个字符')])
    type = SelectField('类别', validators=[DataRequired('请选择类别')], coerce=int)
    rent = IntegerField('价格', validators=[DataRequired('请输入商品价格')])
    cash_pledge = IntegerField('押金', validators=[Optional()])
    size = StringField('尺码', validators=[Length(-1, 64, '尺码内容不超过64个字符')])
    brand = StringField('品牌', validators=[Length(-1, 64, '品牌名不超过64个字符')])
    quantity = IntegerField('库存', validators=[Optional()])
    details = TextAreaField('详情', validators=[Length(-1, 500, '详情描述不超过500个字符')])

    def __init__(self, *args, **kwargs):
        super(GoodsForm, self).__init__(*args, **kwargs)
        self.type.choices = [(-1, '请选择类别...')]+[(one.id, one.name) for one in GoodsType.query.all()]

    def validate_type(self, field):
        if field.data == -1:
            raise ValidationError('请选择类别')

    def set_data(self, goods_obj):
        self.name.data = goods_obj.name
        self.type.data = goods_obj.type_id or -1
        self.rent.data = goods_obj.rent
        self.cash_pledge.data = goods_obj.cash_pledge
        self.size.data = goods_obj.size
        self.brand.data = goods_obj.brand
        self.quantity.data = goods_obj.quantity
        self.details.data = goods_obj.details


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[Length(-1, 8, '用户名不超过8个字符')])
    email = StringField('邮箱', validators=[DataRequired('请输入正确的邮箱地址'), Email('请输入正确的邮箱地址')])
    password = PasswordField('新密码')
    phone_number = StringField('手机号码', validators=[Length(-1, 14, '手机号码不超过14个字符'), Regexp(r'^\d*?$', message='请输入正确的手机号码')])
    resume = TextAreaField('简介', validators=[Length(-1, 500, '简介不超过500个字符')])

    def validate_username(self, field):
        if User.query.filter(User.id != current_user.id, User.username == field.data).count() > 0:
            raise ValidationError('该用户名已被使用')

    def set_data(self):
        self.username.data = current_user.username
        self.email.data = current_user.email
        self.phone_number.data = current_user.phone_number
        self.resume.data = current_user.resume
