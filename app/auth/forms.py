from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from wtforms import ValidationError

from app.models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[Email('请输入正确的邮箱地址')])
    password = PasswordField('密码', validators=[DataRequired('请输入密码')])
    submit = SubmitField('登录')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate_email(self, field):
        user_ = User.query.filter_by(email=field.data).first()
        if user_:
            self.user = user_
        else:
            raise ValidationError('该帐号不存在')

    def validate_password(self, field):
        if self.user:
            if not self.user.verify_password(field.data):
                raise ValidationError('密码输入错误')
