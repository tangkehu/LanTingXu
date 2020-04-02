import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import AnonymousUserMixin, UserMixin
from flask import current_app
from sqlalchemy import func

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    # login_manager加载用户的回掉函数
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    # 重写匿名用户，为其添加权限认证的方法
    def can(self, permission):
        return False

    # 为匿名用户添加商品统计方法
    def get_goods_stat(self):
        return {'total': 0, 'out': 0, 'views': 0}

    # 为匿名用户添加背景图
    @property
    def bg_image(self):
        return '../img/bg-masthead.jpg'


# 装载匿名用户
login_manager.anonymous_user = AnonymousUser


# 多对多关联关系连接表
relation_user_role = db.Table(
    'relation_user_role',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


relation_role_permission = db.Table(
    'relation_role_permission',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    phone_number = db.Column(db.String(14))
    wei_number = db.Column(db.String(32))
    qq_number = db.Column(db.String(16))
    resume = db.Column(db.Text)
    bg_image = db.Column(db.String(128), default='../img/bg-masthead.jpg')
    create_time = db.Column(db.DateTime, default=datetime.now)

    goods = db.relationship('Goods', backref='user', lazy='dynamic')
    goods_img = db.relationship('GoodsImg', backref='user', lazy='dynamic')
    orders = db.relationship('SalesOrder', backref='user', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if not self.roles.all():
            if self.email in current_app.config['ADMINS']:
                self.roles.append(Role.query.filter_by(name='超级管理员').first_or_404())
            else:
                self.roles.append(Role.query.filter_by(name='普通用户').first_or_404())

    # 密码处理
    @property    # 为方法添加只读属性（使方法可以像类属性一样读取）装饰器
    def password(self):    # 使读取值时报错，即不让直接读取该值
        return AttributeError('password是不可读的属性')

    @password.setter    # 为类属性添加赋值方法，即给该属性赋值时自动调用此方法
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def admin_user():
        return User.query.join(
            relation_user_role, (relation_user_role.c.user_id == User.id)).filter(
            relation_user_role.c.role_id == Role.query.filter_by(name='超级管理员').first().id).first()

    def can(self, permission):
        # 典型的join联表查询
        # 权限查询
        return Permission.query.join(
            relation_role_permission, (relation_role_permission.c.permission_id == Permission.id)).join(
            relation_user_role, (relation_user_role.c.role_id == relation_role_permission.c.role_id)).filter(
            relation_user_role.c.user_id == self.id, Permission.name == permission).count() > 0

    @staticmethod
    def add(email, password):
        db.session.add(User(email=email, password=password))
        db.session.commit()

    def edit(self, **kwargs):
        self.username = kwargs.get('username')
        self.email = kwargs.get('email')
        self.phone_number = kwargs.get('phone_number')
        self.wei_number = kwargs.get('wei_number')
        self.qq_number = kwargs.get('qq_number')
        self.resume = kwargs.get('resume')
        if kwargs.get('password'):
            self.password = kwargs.get('password')
        db.session.add(self)
        db.session.commit()

    def change_password(self, password):
        self.password = password
        db.session.add(self)
        db.session.commit()

    def change_bg_image(self, image_name):
        try:
            if self.bg_image != '../img/bg-masthead.jpg':
                os.remove(os.path.join(current_app.config['BG_IMG_PATH'], self.bg_image))
        except Exception as e:
            current_app.logger.info(e)
        self.bg_image = image_name
        db.session.add(self)
        db.session.commit()

    def append_role(self, role_id):
        if not self.exist_role(role_id):
            self.roles.append(Role.query.get_or_404(role_id))
            db.session.add(self)
            db.session.commit()

    def remove_role(self, role_id):
        if self.exist_role(role_id):
            self.roles.remove(Role.query.get_or_404(role_id))
            db.session.add(self)
            db.session.commit()

    def exist_role(self, role_id):
        return self.roles.filter(Role.id == role_id).count() > 0

    def get_goods_stat(self):
        from app.models import Goods
        return {
            'total': self.goods.count(),
            'out': self.goods.filter(Goods.status == False).count(),
            'views': db.session.query(func.sum(Goods.view_count)).filter(Goods.user_id == self.id).scalar() or 0
        }

    def delete(self):
        for item in self.goods.all():
            item.delete()
        for item in self.goods_img.all():
            item.delete()
        db.session.delete(self)
        db.session.commit()


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    details = db.Column(db.Text)

    users = db.relationship('User',
                            secondary=relation_user_role,
                            backref=db.backref('roles', lazy='dynamic'),
                            lazy='dynamic')

    @staticmethod
    def insert_basic_role():
        """ 初始化系统时创建基础角色 """
        basic_role = [{'name': '超级管理员', 'details': '最高级的管理员'},
                      {'name': '普通用户', 'details': '普通注册用户'}]
        for item in basic_role:
            if Role.query.filter_by(name=item['name']).count() is 0:
                db.session.add(Role(name=item['name'], details=item['details']))
        db.session.commit()

    @staticmethod
    def update_admins_permission():
        """ 更新权限后更新超级管理员的权限 """
        admins_role = Role.query.filter_by(name='超级管理员').first_or_404()
        admins_role.permissions = Permission.query.all()
        db.session.add(admins_role)
        db.session.commit()

    def add(self, name, details):
        self.name = name
        self.details = details
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def append_permission(self, permission_id):
        if not self.exist_permission(permission_id):
            self.permissions.append(Permission.query.get_or_404(int(permission_id)))
            db.session.add(self)
            db.session.commit()

    def remove_permission(self, permission_id):
        if self.exist_permission(permission_id):
            self.permissions.remove(Permission.query.get_or_404(int(permission_id)))
            db.session.add(self)
            db.session.commit()

    def exist_permission(self, permission_id):
        return self.permissions.filter(Permission.id == permission_id).count() > 0


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    details = db.Column(db.Text)

    roles = db.relationship('Role',
                            secondary=relation_role_permission,
                            backref=db.backref('permissions', lazy='dynamic'),
                            lazy='dynamic')

    @staticmethod
    def update_permissions():
        """ 在有新权限的时候使用此方法更新权限 """
        update_status = False
        for item in current_app.config['PERMISSIONS']:
            if Permission.query.filter_by(name=item[0]).count() is 0:
                db.session.add(Permission(name=item[0], details=item[1]))
                update_status = True
        if update_status is True:
            db.session.commit()
            Role.update_admins_permission()
