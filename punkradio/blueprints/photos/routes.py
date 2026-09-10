import os
import uuid
from flask import render_template, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from punkradio.extensions import db
from punkradio.forms import GigPhotoForm
from punkradio.models import GigPhoto, Gig
from . import bp


@bp.get("/")
def gallery():
    photos = (
        GigPhoto.query.filter_by(is_approved=True)
        .order_by(GigPhoto.created_at.desc())
        .all()
    )
    return render_template("photos/gallery.html", photos=photos)


@bp.route("/pridat", methods=["GET", "POST"])
def submit_photo():
    form = GigPhotoForm()
    # nabídneme výběr z posledních koncertů (volitelné, fotka může být i bez přiřazení)
    recent_gigs = Gig.query.order_by(Gig.date.desc()).limit(30).all()

    if form.validate_on_submit():
        if form.website.data:
            flash("Díky za fotku!", "success")
            return redirect(url_for("photos.submit_photo"))

        file = form.photo.data
        ext = secure_filename(file.filename).rsplit(".", 1)[-1].lower()
        allowed = current_app.config.get("ALLOWED_PHOTO_EXTENSIONS", {"jpg", "jpeg", "png", "webp"})
        if ext not in allowed:
            flash("Nepodporovaný formát souboru.", "error")
            return render_template("photos/submit.html", form=form, recent_gigs=recent_gigs)

        filename = f"{uuid.uuid4().hex}.{ext}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        gig_id = None
        from flask import request
        raw_gig_id = request.form.get("gig_id")
        if raw_gig_id and raw_gig_id.isdigit():
            gig_id = int(raw_gig_id)

        photo = GigPhoto(
            gig_id=gig_id,
            uploader_name=form.uploader_name.data.strip(),
            caption=(form.caption.data or "").strip() or None,
            filename=filename,
            is_approved=False,
        )
        db.session.add(photo)
        db.session.commit()
        flash("Díky! Fotka čeká na schválení, pak se objeví v galerii.", "success")
        return redirect(url_for("photos.submit_photo"))

    return render_template("photos/submit.html", form=form, recent_gigs=recent_gigs)
