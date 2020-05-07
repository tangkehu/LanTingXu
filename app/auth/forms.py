from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp
from wtforms import ValidationError

from app.models import User


class LoginForm(FlaskForm):
    account = StringField('账号', validators=[DataRequired('请输入正确的账号')])
    password = PasswordField('密码', validators=[DataRequired('请输入密码')])
    submit = SubmitField('登录')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate_account(self, field):
        _filter = [User.email, User.username, User.phone_number, User.wei_number, User.qq_number]
        for one in _filter:
            user_ = User.query.filter(one == field.data).first()
            if user_:
                self.user = user_
                break
        if not self.user:
            raise ValidationError('该账号不存在')

    def validate_password(self, field):
        if self.user:
            if not self.user.verify_password(field.data):
                raise ValidationError('密码输入错误')


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired('请设置您的用户名'), Length(1, 16, '用户名不超过16个字符')])
    phone_number = StringField(
        '手机号码',
        validators=[
            DataRequired('请输入您的手机号码'),
            Length(11, message='手机号码不超过11个字符'),
            Regexp(r'^\d*?$', message='请输入正确的手机号码')
        ]
    )
    password = PasswordField('密码', validators=[DataRequired('请输入密码')])
    password_check = PasswordField(
        '再次输入密码', validators=[DataRequired('请再次输入密码'), EqualTo('password', '两次密码输入不一致')])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).count() > 0:
            raise ValidationError('该用户名已被注册')

    def validate_phone_number(self, field):
        if User.query.filter_by(phone_number=field.data).count() > 0:
            raise ValidationError('该手机号码已被使用')
