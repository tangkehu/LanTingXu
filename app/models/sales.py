import time
from app import db


class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(20))
    price = db.Column(db.Float)
    real_price = db.Column(db.Float)
    pledge = db.Column(db.Float)
    real_pledge = db.Column(db.Float)
    total_real = db.Column(db.Float)
    pay_type = db.Column(db.String(32))
    pay_status = db.Column(db.Boolean)
    delivery_status = db.Column(db.Boolean)
    status = db.Column(db.Boolean)
    remarks = db.Column(db.Text)
    hide_remarks = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    goods = db.relationship('RelationOrderGoods', backref='order', lazy='dynamic')

    def salesman_add(self):
        db.session.add(self)
        db.session.commit()
        self.number = str(int(time.time()))+'{:0>5}'.format(self.id)

    def manager_add(self, goods: dict, real_price: float, real_pledge: float, pay_type, remarks):
        pass


class RelationOrderGoods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'))
