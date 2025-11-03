from flask import render_template
from . import bp

@bp.route("/kontakt")
def index():
    return render_template("kontakt/index.html")
