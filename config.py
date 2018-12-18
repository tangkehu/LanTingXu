import os


class Config:
    SECRET_KEY = 'secret_key'
    GOODS_IMG_PATH = os.path.join(os.getcwd(), 'app'+os.sep+'static'+os.sep+'img_goods')


class DevelopmentConfig(Config):
    SERVER_NAME = 'lanting.com'  # 用于配置子域名以及url_for生成完整的URL


class ProductionConfig(Config):
    SERVER_NAME = 'lanting.live'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
