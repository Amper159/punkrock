from xml.sax.saxutils import escape
from flask import Blueprint, render_template, abort, Response, url_for, request
from punkradio.models import Article, Comment
from punkradio.forms import CommentForm

bp = Blueprint("news", __name__, url_prefix="/novinky")

_CATEGORIES = {
    "novinka": "Novinky",
    "rozhovor": "Rozhovory",
    "recenze": "Recenze",
}

@bp.route("/")
def list_news():
    category = request.args.get("kategorie")
    query = Article.query
    if category in _CATEGORIES:
        query = query.filter_by(category=category)
    articles = query.order_by(Article.published_at.desc()).all()
    return render_template(
        "news/index.html", articles=articles,
        active_category=category, categories=_CATEGORIES,
    )

@bp.route("/<slug>")
def detail(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        abort(404)
    comments = (
        Comment.query
        .filter_by(target_type="article", target_id=article.id, is_approved=True)
        .order_by(Comment.created_at.asc())
        .all()
    )
    comment_form = CommentForm()
    return render_template("news/detail.html", article=article, comments=comments, comment_form=comment_form)


@bp.route("/rss.xml")
def rss():
    articles = Article.query.order_by(Article.published_at.desc()).limit(30).all()

    items = []
    for a in articles:
        link = a.source_url or url_for("news.detail", slug=a.slug, _external=True)
        description = a.perex or ""
        pub_date = a.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
        items.append(f"""    <item>
      <title>{escape(a.title)}</title>
      <link>{escape(link)}</link>
      <guid isPermaLink="false">news-{a.id}</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{escape(description)}</description>
    </item>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Punkrock 77 — novinky</title>
    <link>{escape(url_for('news.list_news', _external=True))}</link>
    <description>Punkové novinky — desky, koncerty, rozhovory a drby ze scény.</description>
    <language>cs</language>
{chr(10).join(items)}
  </channel>
</rss>
"""
    return Response(xml, mimetype="application/rss+xml")
