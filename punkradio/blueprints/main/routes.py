from flask import Blueprint, render_template
from punkradio.models import Gig, Article, Band
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
    articles = (
        Article.query
        .order_by(Article.published_at.desc())
        .limit(3)
        .all()
    )
    bands = (
        Band.query.filter_by(is_approved=True)
        .order_by(Band.created_at.desc())
        .limit(6)
        .all()
    )

    # 🎸 Kapela měsíce — deterministický výběr podle měsíce, mění se samo bez zásahu
    all_approved = Band.query.filter_by(is_approved=True).order_by(Band.id.asc()).all()
    band_of_month = None
    if all_approved:
        idx = (today.year * 12 + today.month) % len(all_approved)
        band_of_month = all_approved[idx]

    return render_template(
        "main/index.html", gigs=gigs, articles=articles, bands=bands, band_of_month=band_of_month
    )

