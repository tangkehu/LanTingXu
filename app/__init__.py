import os
from flask import Flask

from config import config


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'production')
    app.config.from_object(config[config_name])

    from .main import main_bp
    app.register_blueprint(main_bp)

    from .goods import goods_bp
    app.register_blueprint(goods_bp, subdomain='goods')

    return app
