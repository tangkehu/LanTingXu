from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError

from app.models import User


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[Length(-1, 8, '用户名不超过8个字符')])
    email = StringField('邮箱', validators=[DataRequired('请输入正确的邮箱地址'), Email('请输入正确的邮箱地址')])
    password = PasswordField('新密码')
    phone_number = StringField('手机号码', validators=[Length(-1, 14, '手机号码不超过14个字符'), Regexp(r'^\d*?$', message='请输入正确的手机号码')])
    resume = TextAreaField('简介', validators=[Length(-1, 500, '简介不超过500个字符')])

    def __init__(self, user_obj, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user_obj = user_obj

    def validate_username(self, field):
        if User.query.filter(User.id != self.user_obj.id, User.username == field.data).count() > 0:
            raise ValidationError('该用户名已被使用')

    def set_data(self):
        self.username.data = self.user_obj.username
        self.email.data = self.user_obj.email
        self.phone_number.data = self.user_obj.phone_number
        self.resume.data = self.user_obj.resume


class HomePageForm(FlaskForm):
    caption = StringField('标题', validators=[DataRequired('请输入标题内容')])
    subhead = TextAreaField('副标题', validators=[DataRequired('请输入副标题内容')])
    about = TextAreaField('关于我们', validators=[DataRequired('请输入关于我们的内容')])
    statement = TextAreaField('声明', validators=[DataRequired('请输入声明内容')])
    # bg_img = FileField('背景图', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只能上传图片')])
