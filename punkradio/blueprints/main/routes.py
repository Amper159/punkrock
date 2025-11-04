from flask import Blueprint, render_template
from punkradio.models import Gig
from datetime import date

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    gigs = gigs = Gig.query.order_by(Gig.date).limit(4).all()
    print("DEBUG – načteno koncertů:", len(gigs))  # <- tohle je důležité!
    return render_template("main/index.html", gigs=gigs)
