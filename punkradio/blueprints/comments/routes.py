from flask import redirect, url_for, flash, request, abort
from punkradio.extensions import db
from punkradio.forms import CommentForm
from punkradio.models import Comment, Gig, Article
from . import bp

_ALLOWED_TARGETS = {"gig", "article"}


@bp.post("/<target_type>/<int:target_id>")
def add_comment(target_type, target_id):
    if target_type not in _ALLOWED_TARGETS:
        abort(404)

    # ověřit, že cíl komentáře reálně existuje
    if target_type == "gig":
        target = Gig.query.get(target_id)
        redirect_url = url_for("gigs.gigs_list", _anchor=f"gig-{target_id}")
    else:
        target = Article.query.get(target_id)
        redirect_url = url_for("news.detail", slug=target.slug) if target else url_for("news.list_news")

    if not target:
        abort(404)

    form = CommentForm()
    if form.validate_on_submit():
        if form.website.data:
            # honeypot vyplněný = bot, tváříme se že je vše OK a nic neukládáme
            flash("Díky za komentář!", "success")
            return redirect(redirect_url)

        comment = Comment(
            target_type=target_type,
            target_id=target_id,
            author_name=form.author_name.data.strip(),
            text=form.text.data.strip(),
        )
        db.session.add(comment)
        db.session.commit()
        flash("Díky za komentář!", "success")
    else:
        flash("Komentář se nepodařilo přidat — zkontroluj vyplněná pole.", "error")

    return redirect(redirect_url)
