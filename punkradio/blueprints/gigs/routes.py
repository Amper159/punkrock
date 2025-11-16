from datetime import date
from flask import Blueprint
from flask import render_template
from punkradio.models import Gig


bp = Blueprint('gigs', __name__)

@bp.route("/")
def gigs_list():
    # Zobraz pouze koncerty, které se ještě neuskutečnily
    gigs = (
        Gig.query
        .filter(Gig.date >= date.today())
        .order_by(Gig.date.asc())
        .all()
    )
    return render_template("gigs/list.html", gigs=gigs)




