from datetime import date
from flask import Blueprint
from flask import render_template
from punkradio.models import Gig


bp = Blueprint("gigs", __name__, url_prefix="/koncerty")

@bp.route("/")
def gigs_list():
    today = date.today()

    # 🎸 Jen budoucí koncerty, seřazené podle data
    gigs = (
        Gig.query
        .filter(Gig.date >= today)
        .order_by(Gig.date.asc())
        .all()
    )

    return render_template("gigs/koncerty.html", gigs=gigs, today=today)



