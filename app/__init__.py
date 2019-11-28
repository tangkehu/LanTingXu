import os
import click
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_login import LoginManager

from config import config
from .utils import SSLSMTPHandler, goods_img_ratio, goods_order_map

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth_bp.login'
login_manager.login_message = '请登录账号。'


def create_app(config_name=os.getenv('FLASK_CONFIG', 'production')):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    register_logging(app)
    register_blueprints(app)
    register_errors(app)
    register_template_context(app)
    register_click(app)

    return app


def register_click(app):
    @app.cli.command()
    def deploy():
        """ 部署，部署前请创建数据库迁移脚本flask db migrate """
        # upgrade()  # 数据库更新

        # from .models import Role
        # Role.insert_basic_role()  # 初始化系统时插入基础角色
        # from .models import Permission
        # Permission.update_permissions()  # 系统初始化时开启，或在有新权限的时候开启

        from .models import Goods

        for one in Goods.query.all():
            one.view_count = 0
            db.session.add(one)
        db.session.commit()

        click.echo(u'本次部署初始化成功')


def register_blueprints(app):
    from .main import main_bp
    app.register_blueprint(main_bp)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from .goods import goods_bp
    app.register_blueprint(goods_bp, url_prefix='/goods')

    from .manage import manage_bp
    app.register_blueprint(manage_bp, url_prefix='/manage')

    from .sales import sales_bp
    app.register_blueprint(sales_bp, url_prefix='/sales')

    from .user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')


def register_errors(app):
    @app.errorhandler(403)
    def forbid_error(e):
        return render_template('404.html'), 403

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('404.html'), 500


def register_template_context(app):
    """ 注册全局变量以供jinja2模板使用 """

    @app.context_processor
    def inject_context():
        from .models import GoodsType

        return dict(
            BOOT_CDN=app.config['BOOT_CDN'],   # 是否启用boot cdn
            SYS_NAME=app.config['SYS_NAME'],  # 系统名称
            TYPE_LI=GoodsType.query.all(),  # 商品类型列表
            goods_img_ratio=goods_img_ratio,  # 商品比例计算方法
            goods_order_map=goods_order_map  # 商品排序MAP
        )


def register_logging(app):
    if not app.debug:
        if app.config.get('MAIL_SERVER'):
            mail_handler = SSLSMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                          credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
                                          fromaddr=app.config['MAIL_SENDER'], toaddrs=app.config['MAIL_ADMINS'],
                                          subject='兰亭续官网 ERRORS 警报日志')
            mail_handler.setFormatter(logging.Formatter('''
                Message type:       %(levelname)s
                Location:           %(pathname)s:%(lineno)d
                Module:             %(module)s
                Function:           %(funcName)s
                Time:               %(asctime)s

                Message:

                %(message)s
                '''))
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/run.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
