import os
from datetime import datetime
from flask_login import current_user
from flask import current_app

from app import db
from app.utils import random_filename, resize_img


class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    rent = db.Column(db.Integer)
    cash_pledge = db.Column(db.Integer)
    brand = db.Column(db.String(64))
    size = db.Column(db.String(64))
    details = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    updata_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    img = db.relationship('GoodsImg', backref='goods', lazy='dynamic')

    def add(self, name, rent, user=current_user, **kwargs):
        self.name = name
        self.rent = rent
        self.cash_pledge = kwargs.get('cash_pledge')
        self.size = kwargs.get('size')
        self.brand = kwargs.get('brand')
        self.details = kwargs.get('details')
        self.user = user
        self.img = GoodsImg.query.filter_by(status=False, user_id=user.id).all()
        db.session.add(self)
        db.session.commit()
        for item in GoodsImg.query.filter_by(status=False, user_id=user.id).all():
            item.alter_status()

    def edit(self, name, rent, **kwargs):
        self.name = name
        self.rent = rent
        self.cash_pledge = kwargs.get('cash_pledge')
        self.size = kwargs.get('size')
        self.brand = kwargs.get('brand')
        self.details = kwargs.get('details')
        self.updata_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        for item in self.img.all():
            item.delete()
        db.session.delete(self)
        db.session.commit()


class GoodsImg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), unique=True, nullable=False)
    filename_m = db.Column(db.String(128), unique=True, nullable=False)
    filename_s = db.Column(db.String(128), unique=True, nullable=False)
    status = db.Column(db.Boolean, default=False)  # 0 未与商品关联，1 已与商品关联
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))

    def add(self, file_object, goods_id=None, status=False, user=current_user, user_id=None):
        from . import User
        img_allow = ['.jpg', '.jpeg', '.png', '.gif']
        if os.path.splitext(file_object.filename)[1] not in img_allow:
            return {'status': False, 'msg': '不支持的图片格式'}
        filename = random_filename(file_object.filename)
        file_object.save(os.path.join(current_app.config['GOODS_IMG_PATH'], filename))
        filename_m = resize_img(current_app.config['GOODS_IMG_PATH'], filename, 400)
        filename_s = resize_img(current_app.config['GOODS_IMG_PATH'], filename, 200)
        self.filename = filename
        self.filename_m = filename_m
        self.filename_s = filename_s
        self.status = status
        self.user = user if user_id is None else User.query.get_or_404(int(user_id))
        if goods_id:
            self.goods = Goods.query.get_or_404(int(goods_id))
            self.status = True
        db.session.add(self)
        db.session.commit()
        return {'status': True, 'msg': '添加成功', 'img_obj': self}

    def alter_status(self):
        self.status = True if self.status is False else False
        db.session.add(self)
        db.session.commit()

    def delete(self):
        os.remove(os.path.join(current_app.config['GOODS_IMG_PATH'], self.filename))
        try:
            os.remove(os.path.join(current_app.config['GOODS_IMG_PATH'], self.filename_m))
            os.remove(os.path.join(current_app.config['GOODS_IMG_PATH'], self.filename_s))
        except Exception as e:
            pass
        db.session.delete(self)
        db.session.commit()
