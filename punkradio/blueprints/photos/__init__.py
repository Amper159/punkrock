from flask import Blueprint

bp = Blueprint("photos", __name__)

from . import routes
