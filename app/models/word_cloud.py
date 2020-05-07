
import datetime
from app import db


class WordCloud(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(128))
    count = db.Column(db.Integer, default=1)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now)

    @staticmethod
    def upsert(word):
        """
        按照搜索词，有就更新，没有就新增
        :param word: 搜索词
        :return:
        """
        _word_obj = WordCloud.query.filter_by(word=word).first()
        if _word_obj:
            _word_obj.count += 1
            _word_obj.update_time = datetime.datetime.now()
        else:
            _word_obj = WordCloud(word=word)
        db.session.add(_word_obj)
        db.session.commit()

    @staticmethod
    def query_for_max_on_window(window, limit=10):
        """
        查询指定时间窗口的搜索关键词，按搜索量降序排序
        :param window: int类型 时间窗口/天
        :param limit: 查询的数量
        :return: [word_count_obj, ]
        """
        stop_datetime = datetime.datetime.now()
        start_datetime = stop_datetime - datetime.timedelta(days=window)
        result = WordCloud.query.\
            filter(WordCloud.update_time <= stop_datetime, WordCloud.update_time >= start_datetime).\
            order_by(WordCloud.count.desc()).limit(limit).all()
        return result
