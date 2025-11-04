from flask import Blueprint, render_template
from punkradio.models import Gig
from datetime import date

bp = Blueprint("gigs", __name__)

def get_upcoming_concerts(limit=4):
    today = date.today()
    return Gig.query.filter(Gig.date >= today).order_by(Gig.date.asc()).limit(limit).all()

@bp.route("/koncerty")
def koncerty():
    concerts = Gig.query.order_by(Gig.date.asc()).all()
    return render_template("gigs/index.html", concerts=concerts)



