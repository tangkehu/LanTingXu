from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo
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
        user_ = User.query.filter_by(email=field.data).first()
        if not user_:
            user_ = User.query.filter_by(username=field.data).first()
        if not user_:
            user_ = User.query.filter_by(phone_number=field.data).first()
        if user_:
            self.user = user_
        else:
            raise ValidationError('该账号不存在')

    def validate_password(self, field):
        if self.user:
            if not self.user.verify_password(field.data):
                raise ValidationError('密码输入错误')


class RegisterForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired('请输入正确的邮箱地址'), Email('请输入正确的邮箱地址')])
    password = PasswordField('密码', validators=[DataRequired('请输入密码')])
    password_check = PasswordField('再次输入密码', validators=[DataRequired('请再次输入密码'), EqualTo('password', '两次密码输入不一致')])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).count() > 0:
            raise ValidationError('该邮箱账号已被注册')
