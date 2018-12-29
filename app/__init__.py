import os
import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_login import LoginManager

from config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth_bp.login'
login_manager.login_message = '请登录账号。'


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @app.cli.command()
    def deploy():
        """ 部署，部署前请创建数据库迁移脚本flask db migrate """
        from .models import Goods

        upgrade()

        for item in Goods.query.all():
            # 添加size字段时使用，使用后删除
            item.size = item.brand
            item.brand = None
            db.session.add(item)
        db.session.commit()

        click.echo(u'本次部署初始化成功')

    from .main import main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(main_bp, subdomain='www')

    from .auth import auth_bp
    app.register_blueprint(auth_bp, subdomain='auth')

    from .goods import goods_bp
    app.register_blueprint(goods_bp, subdomain='goods')

    return app
