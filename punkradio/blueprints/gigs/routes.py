from flask import Blueprint, render_template, request
from punkradio.models import Gig
from datetime import date

bp = Blueprint("gigs", __name__)

@bp.get("/")
def list_gigs():
    city = request.args.get("city")
    q = Gig.query.filter(Gig.date >= date.today())
    if city:
        q = q.filter(Gig.city.ilike(f"%{city}%"))
    gigs = q.order_by(Gig.date.asc()).all()
    return render_template("gigs/index.html", gigs=gigs)
