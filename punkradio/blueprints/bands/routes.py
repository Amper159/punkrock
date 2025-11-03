from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from punkradio.forms import BandSubmitForm
from punkradio.extensions import db
from punkradio.models import Band
import smtplib
from email.message import EmailMessage

bp = Blueprint("bands", __name__)

@bp.get("/")
def list_bands():
    bands = (Band.query.filter_by(is_approved=True)
                      .order_by(Band.created_at.desc())
                      .all())
    return render_template("bands/index.html", bands=bands)

@bp.route("/pridat", methods=["GET", "POST"])
def submit_band():
    form = BandSubmitForm()
    if form.validate_on_submit():
        band = Band(
            name=form.name.data.strip(),
            city=(form.city.data or "").strip() or None,
            styles=(form.styles.data or ""),
            about=form.about.data,
            links={
                "spotify": form.spotify.data,
                "bandcamp": form.bandcamp.data,
                "web": form.web.data,
            },
            is_approved=False,
        )
        db.session.add(band)
        db.session.commit()
        _notify_admin_new_band(band)
        flash("Díky! Kapela byla odeslána ke schválení.", "success")
        return redirect(url_for("bands.list_bands"))
    return render_template("bands/submit.html", form=form)

def _notify_admin_new_band(band: Band):
    cfg = current_app.config
    if not all([cfg.get("ADMIN_EMAIL"), cfg.get("SMTP_HOST"), cfg.get("SMTP_USER"), cfg.get("SMTP_PASS")]):
        return
    msg = EmailMessage()
    msg["Subject"] = f"[Punkrock rádio] Nová kapela: {band.name}"
    msg["From"] = cfg["SMTP_USER"]
    msg["To"] = cfg["ADMIN_EMAIL"]
    msg.set_content(
        f"Název: {band.name}\nMěsto: {band.city or '-'}\nStyly: {band.styles or '-'}\nOdkazy: {band.links or '-'}\n"
        "Pozn.: is_approved=False (schval v DB nebo admin rozhraní)."
    )
    with smtplib.SMTP(cfg["SMTP_HOST"], int(cfg.get("SMTP_PORT", 587))) as s:
        s.starttls()
        s.login(cfg["SMTP_USER"], cfg["SMTP_PASS"])
        s.send_message(msg)
