
from datetime import datetime
from app import db


class WxUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    last_time = db.Column(db.Date, default=datetime.now)
    flag = db.Column(db.Boolean, default=False)

    @staticmethod
    def validate_time(username):
        """ 验证最后一次的请求时间间隔是否超过5分钟, 超过为True """

        user = WxUser.query.filter_by(username=username).first()
        if user:
            last_time = user.last_time
            user.update_time()
            return True if (datetime.now() - last_time).total_seconds() > 300 else False
        else:
            db.session.add(WxUser(username=username))
            db.session.commit()
            return True

    def update_time(self):
        self.last_time = datetime.now()
        db.session.add(self)
        db.session.commit()
