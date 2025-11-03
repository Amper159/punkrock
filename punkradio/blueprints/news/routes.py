from flask import Blueprint, render_template, abort
from punkradio.models import Article

bp = Blueprint("news", __name__)

@bp.get("/")
def list_news():
    items = Article.query.order_by(Article.published_at.desc()).all()
    return render_template("news/index.html", items=items)

@bp.get("/<slug>")
def detail(slug):
    item = Article.query.filter_by(slug=slug).first()
    if not item:
        abort(404)
    return render_template("news/detail.html", item=item)
