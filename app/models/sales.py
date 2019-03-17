from datetime import datetime
from flask_login import current_user
from sqlalchemy import cast, extract, DATE, func
from app import db


class SalesOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    pledge = db.Column(db.Float)
    total_real = db.Column(db.Float)
    pay_type = db.Column(db.String(32))
    pay_status = db.Column(db.Boolean, default=False)
    delivery_status = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer, default=1)
    remarks = db.Column(db.Text)
    hide_remarks = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    goods = db.relationship('RelationOrderGoods', backref='order', lazy='dynamic')

    def salesman_add(self) -> int:
        self.pay_status = False
        self.delivery_status = True
        self.status = 0
        self.remarks = u'线下销售订单'
        self.user = current_user._get_current_object()
        db.session.add(self)
        db.session.commit()
        self.sum_price()
        return self.id

    def salesman_update(self, total_real: float, pay_type: str, pay_status: bool, remarks: str):
        self.total_real = total_real
        self.pay_type = pay_type
        self.pay_status = pay_status
        self.remarks = remarks
        self.create_time = datetime.now()
        self.status = 2 if self.pay_status and self.delivery_status else 1
        db.session.add(self)
        db.session.commit()

    def salesman_close(self):
        self.status = 0
        db.session.add(self)
        db.session.commit()

    def salesman_goods_append(self, goods_id: int):
        from . import Goods
        relation = self.goods.filter_by(goods_id=goods_id).first()
        if relation:
            relation.count += 1
            db.session.add(relation)
        else:
            db.session.add(RelationOrderGoods(count=1, order=self, goods=Goods.query.get_or_404(goods_id)))
        db.session.commit()
        self.sum_price()

    def salesman_goods_remove(self, goods_id: int, is_delete=False):
        relation = self.goods.filter_by(goods_id=goods_id).first()
        if relation:
            if is_delete is False and relation.count > 1:
                relation.count -= 1
                db.session.add(relation)
            else:
                self.goods.remove(relation)
                db.session.add(self)
            db.session.commit()
            self.sum_price()

    def sum_price(self):
        price = 0
        pledge = 0
        for item in self.goods.all():
            goods_price = item.goods.price
            goods_pledge = item.goods.cash_pledge
            if goods_price:
                price += goods_price*item.count
            if goods_pledge:
                pledge += goods_pledge*item.count
        self.price = price
        self.pledge = pledge
        self.total_real = price + pledge
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def clear_invalid():
        """ 清理无效订单 """
        for item in SalesOrder.query.filter(SalesOrder.status == 0).all():
            if item.goods.count() == 0:
                db.session.delete(item)
                db.session.commit()

    @staticmethod
    def stat_data(the_type: str, the_date: str) -> dict:
        """ 按照时间进行订单数据统计；这里示例了sql高级查询的方法 """
        # TODO: 各种高级查询方法
        params = [SalesOrder.status != 0]
        if the_type == 'day':
            the_date = datetime.strptime(the_date, '%Y-%m-%d')
            params.append(cast(SalesOrder.create_time, DATE) == the_date.date())
        elif the_type == 'month':
            the_date = datetime.strptime(the_date, '%Y-%m')
            params.append(extract('year', SalesOrder.create_time) == the_date.year)
            params.append(extract('month', SalesOrder.create_time) == the_date.month)
        count_order = SalesOrder.query.filter(*params).count()
        count_pay_false = SalesOrder.query.filter(SalesOrder.pay_status == False, *params).count()
        sum_price = db.session.query(func.sum(SalesOrder.price)).filter(*params).scalar() or 0
        sum_total_real = db.session.query(func.sum(SalesOrder.total_real)).filter(
            SalesOrder.pay_status == True, *params).scalar() or 0
        sum_pay_type = db.session.query(func.sum(SalesOrder.total_real).label('total'), SalesOrder.pay_type).filter(
            SalesOrder.pay_status == True, *params).group_by(SalesOrder.pay_type)
        # 统计各个商品的销售量
        # sum_goods_count = db.session.query(Goods.id, func.sum(RelationOrderGoods.count).label('number')).join(
        #     RelationOrderGoods, RelationOrderGoods.goods_id == Goods.id).join(
        #     SalesOrder, SalesOrder.id == RelationOrderGoods.order_id).filter(
        #     cast(SalesOrder.create_time, DATE) == the_date.date(), SalesOrder.status != 0).group_by(Goods.id)[0:3]

        result = {'count_order': count_order,  # 订单总量
                  'count_pay_false': count_pay_false,  # 未付款订单量
                  'sum_price': sum_price,  # 应收金额，不包括应收押金
                  'sum_total_real': sum_total_real,  # 实收金额
                  'sum_pay_type': list(sum_pay_type)}  # 各收款类别实收
        return result


class RelationOrderGoods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'))
