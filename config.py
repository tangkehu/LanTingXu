import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


class Config:
    SYS_NAME = u'汉服租赁网'
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 不追踪对象的修改，减少内存使用
    GOODS_IMG_PATH = os.path.join(os.getcwd(), 'app'+os.sep+'static'+os.sep+'img_goods')
    PER_PAGE = 20  # 分页查询的每页数据量设置
    ADMINS = ['lantingxuapplet@163.com']
    BOOT_CDN = True  # 是否使用免费快速的bootcdn服务
    PERMISSIONS = [['goods_manage', '管理商品的能力'],
                   ['system_manage', '管理系统的能力'],
                   ['order_manage', '管理订单的能力']]

    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_SENDER = 'www.lanting.live <{}>'.format(MAIL_USERNAME)
    MAIL_ADMINS = ['329937872@qq.com']


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(os.getenv('FLASK_DATABASE_USER'),
                                                                          os.getenv('FLASK_DATABASE_PASSWORD'),
                                                                          os.getenv('FLASK_DATABASE_HOST'),
                                                                          os.getenv('FLASK_DATABASE_NAME'))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(os.getenv('FLASK_DATABASE_USER'),
                                                                          os.getenv('FLASK_DATABASE_PASSWORD'),
                                                                          os.getenv('FLASK_DATABASE_HOST'),
                                                                          os.getenv('FLASK_DATABASE_NAME'))


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
