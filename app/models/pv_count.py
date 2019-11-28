
import datetime
from app import db


class PvCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count_date = db.Column(db.String(10), unique=True, index=True)
    home_count = db.Column(db.Integer, default=0)

    @staticmethod
    def add_home_count():
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        count_obj = PvCount.query.filter_by(count_date=today).first()
        if count_obj:
            count_obj.home_count += 1
        else:
            count_obj = PvCount(home_count=1, count_date=today)
        db.session.add(count_obj)
        db.session.commit()

    @staticmethod
    def get_charts_data():
        date = []
        home_count = []
        for item in range(28):
            _day = datetime.datetime.now() - datetime.timedelta(days=item)
            str_today = _day.strftime("%Y-%m-%d")
            if item is 0:
                date.insert(0, '今天')
            else:
                date.insert(0, str_today)

            count_obj = PvCount.query.filter_by(count_date=str_today).first()
            if count_obj:
                home_count.insert(0, count_obj.home_count)
            else:
                home_count.insert(0, 0)
        return {'date': date, 'home_count': home_count}
