
from datetime import datetime
from app import db


class WxUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    last_time = db.Column(db.DateTime, default=datetime.now)
    flag = db.Column(db.Boolean, default=False)

    @staticmethod
    def validate_time(username):
        """ 验证最后一次发送推广消息的时间间隔是否超过5分钟, 超过为True """

        user = WxUser.query.filter_by(username=username).first()
        if user:
            if (datetime.now() - user.last_time).total_seconds() > 300:
                user.update_time()
                return True
            else:
                return False
        else:
            db.session.add(WxUser(username=username))
            db.session.commit()
            return True

    @staticmethod
    def validate_flag(username):
        """ 验证是否已参加活动 """
        user = WxUser.query.filter_by(username=username).first()
        if user:
            if user.flag is False:
                user.update_flag()
                return False
            else:
                return True
        else:
            db.session.add(WxUser(username=username, flag=True))
            db.session.commit()
            return False

    def update_time(self):
        self.last_time = datetime.now()
        db.session.add(self)
        db.session.commit()

    def update_flag(self):
        self.flag = True if self.flag is False else False
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def init_flag():
        for item in WxUser.query.filter_by(flag=True).all():
            item.flag = False
            db.session.add(item)
        db.session.commit()
