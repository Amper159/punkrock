from flask import Blueprint, render_template
from punkradio.models import Gig
from datetime import date

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    today = date.today()
    gigs = (
        Gig.query
        .filter(Gig.date >= today)
        .order_by(Gig.date.asc())
        .limit(5)
        .all()
    )
    return render_template("main/index.html", gigs=gigs)

