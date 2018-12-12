

class Config:
    SECURE_KEY = 'this is a key.'


class DevelopmentConfig(Config):
    SERVER_NAME = 'lanting.com'


class ProductionConfig(Config):
    SERVER_NAME = 'lanting.live'


config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
