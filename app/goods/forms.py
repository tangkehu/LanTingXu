from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length


class GoodsForm(FlaskForm):
    name = StringField('商品名', validators=[DataRequired('请输入商品名'), Length(1, 64, '商品名不超过64个字符')])
    rent = IntegerField('租金', validators=[DataRequired('请输入租金')])

    def set_data(self, name, rent):
        self.name.data = name
        self.rent.data = rent


class GoodsDeleteForm(FlaskForm):
    goods_id = IntegerField(validators=[DataRequired('未找到要删除的对象。')])
