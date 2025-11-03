from flask import Blueprint, render_template
from punkradio.models import Gig, Article
from datetime import date

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    gigs = (Gig.query.filter(Gig.date >= date.today())
                    .order_by(Gig.date.asc())
                    .limit(4).all())
    news = Article.query.order_by(Article.published_at.desc()).limit(3).all()
    return render_template("main/index.html", gigs=gigs, news=news)
