from flask import Blueprint

manage_bp = Blueprint('manage_bp', __name__)

from . import views
