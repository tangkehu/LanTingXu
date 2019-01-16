import os


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 不追踪对象的修改，减少内存使用
    GOODS_IMG_PATH = os.path.join(os.getcwd(), 'app'+os.sep+'static'+os.sep+'img_goods')

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_SENDER = 'www.lanting.live <{}>'.format(MAIL_USERNAME)
    MAIL_ADMINS = ['329937872@qq.com']


class DevelopmentConfig(Config):
    SERVER_NAME = 'lanting.com'  # 用于配置子域名以及url_for生成完整的URL
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(os.getenv('FLASK_DATABASE_USER'),
                                                                          os.getenv('FLASK_DATABASE_PASSWORD'),
                                                                          os.getenv('FLASK_DATABASE_HOST'),
                                                                          os.getenv('FLASK_DATABASE_NAME'))


class ProductionConfig(Config):
    SERVER_NAME = 'lanting.live'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(os.getenv('FLASK_DATABASE_USER'),
                                                                          os.getenv('FLASK_DATABASE_PASSWORD'),
                                                                          os.getenv('FLASK_DATABASE_HOST'),
                                                                          os.getenv('FLASK_DATABASE_NAME'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
