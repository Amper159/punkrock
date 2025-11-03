from flask import Blueprint

bp = Blueprint("komunita_bp", __name__, template_folder="templates")

from . import routes
