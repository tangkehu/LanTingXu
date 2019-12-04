from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError

from app.models import User


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('请输入用户名'), Length(1, 16, '用户名不超过16个字符')])
    email = StringField('邮箱', validators=[DataRequired('请输入正确的邮箱地址'), Email('请输入正确的邮箱地址')])
    password = StringField('新密码')
    phone_number = StringField('手机号码', validators=[Length(-1, 11, '手机号码不超过11个字符'), Regexp(r'^\d*?$', message='请输入正确的手机号码')])
    wei_number = StringField('微信号', validators=[Length(-1, 32, '微信号码不超过32个字符')])
    qq_number = StringField('QQ号', validators=[Length(-1, 16, 'QQ号码不超过16个字符')])
    resume = TextAreaField('简介', validators=[Length(-1, 500, '简介不超过500个字符')])

    def __init__(self, user_obj, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user_obj = user_obj

    def validate_username(self, field):
        if User.query.filter(User.id != self.user_obj.id, User.username == field.data).count() > 0:
            raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        if User.query.filter(User.id != self.user_obj.id, User.email == field.data).count() > 0:
            raise ValidationError('该邮箱已被使用')

    def validate_phone_number(self, field):
        if field.data and User.query.filter(User.id != self.user_obj.id, User.phone_number == field.data).count() > 0:
            raise ValidationError('该手机号码已被使用')

    def validate_wei_number(self, field):
        if field.data and User.query.filter(User.id != self.user_obj.id, User.wei_number == field.data).count() > 0:
            raise ValidationError('该微信号码已被使用')

    def validate_qq_number(self, field):
        if field.data and User.query.filter(User.id != self.user_obj.id, User.qq_number == field.data).count() > 0:
            raise ValidationError('该QQ号码已被使用')

    def set_data(self):
        self.username.data = self.user_obj.username
        self.email.data = self.user_obj.email
        self.phone_number.data = self.user_obj.phone_number
        self.wei_number.data = self.user_obj.wei_number
        self.qq_number.data = self.user_obj.qq_number
        self.resume.data = self.user_obj.resume


class HomePageForm(FlaskForm):
    caption = StringField('标题', validators=[DataRequired('请输入标题内容')])
    subhead = TextAreaField('副标题', validators=[DataRequired('请输入副标题内容')])
    about = TextAreaField('关于我们', validators=[DataRequired('请输入关于我们的内容')])
    statement = TextAreaField('声明', validators=[DataRequired('请输入声明内容')])

    def set_data(self, obj):
        self.caption.data = obj.caption
        self.subhead.data = obj.subhead
        self.about.data = obj.about
        self.statement.data = obj.statement
