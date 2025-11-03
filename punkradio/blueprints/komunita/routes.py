from flask import render_template
from . import bp

@bp.route("/komunita")
def komunita():
    return render_template("komunita/index.html")
