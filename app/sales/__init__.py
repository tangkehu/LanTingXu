from flask import Blueprint

sales_bp = Blueprint('sales_bp', __name__)

from . import views
