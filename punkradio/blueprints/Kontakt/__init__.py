from flask import Blueprint

bp = Blueprint("kontakt", __name__)

from . import routes
