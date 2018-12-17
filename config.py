

class Config:
    SECRET_KEY = 'secret_key'


class DevelopmentConfig(Config):
    SERVER_NAME = 'lanting.com'  # 用于配置子域名以及url_for生成完整的URL


class ProductionConfig(Config):
    SERVER_NAME = 'lanting.live'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
