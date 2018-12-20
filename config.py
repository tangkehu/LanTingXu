import os


class Config:
    SECRET_KEY = 'secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 不追踪对象的修改，减少内存使用
    GOODS_IMG_PATH = os.path.join(os.getcwd(), 'app'+os.sep+'static'+os.sep+'img_goods')
    ADMIN_EMAIL = '329937872@qq.com'
    ADMIN_PASSWORD = 'tang@1013'


class DevelopmentConfig(Config):
    SERVER_NAME = 'lanting.com'  # 用于配置子域名以及url_for生成完整的URL
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://remote:zylT#1013@47.97.109.179/lanting_test'


class ProductionConfig(Config):
    SERVER_NAME = 'lanting.live'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://remote:zylT#1013@47.97.109.179/lanting'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
