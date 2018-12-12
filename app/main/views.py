from flask import render_template

from . import main_bp


@main_bp.route('/')
@main_bp.route('/', subdomain='www')
def index():
    return render_template('main/index.html')
