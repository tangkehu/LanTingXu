from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import AnonymousUserMixin

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    # login_manager加载用户的回掉函数
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    # 重写匿名用户的权限认证
    def can(self, permission):
        return False


login_manager.anonymous_user = AnonymousUser


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    goods = db.relationship('Goods', backref='user', lazy='dynamic')
    goods_img = db.relationship('GoodsImg', backref='user', lazy='dynamic')

    # def __init__(self, *args, **kwargs):
    #     super(User, self).__init__(*args, **kwargs)

    # 配置flask-login的必需属性
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def insert_basic():
        if not User.query.filter_by(email=current_app.config['ADMIN_EMAIL']).first():
            db.session.add(User(email=current_app.config['ADMIN_EMAIL'],
                                password=current_app.config['ADMIN_PASSWORD']))
            db.session.commit()

    # 密码处理
    @property    # 为方法添加只读属性（使方法可以像类属性一样读取）装饰器
    def password(self):    # 使读取值时报错，即不让直接读取该值
        return AttributeError('password是不可读的属性')

    @password.setter    # 为类属性添加赋值方法，即给该属性赋值时自动调用此方法
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, permission):
        return True
