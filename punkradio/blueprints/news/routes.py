from flask import Blueprint, render_template, abort
from punkradio.models import Article

bp = Blueprint("news", __name__, url_prefix="/novinky")

@bp.route("/")
def list_news():
    articles = Article.query.order_by(Article.published_at.desc()).all()
    return render_template("news/index.html", articles=articles)

@bp.route("/<slug>")
def detail(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        abort(404)
    return render_template("news/detail.html", article=article)
