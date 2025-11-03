from flask import Blueprint, render_template, url_for, current_app
import os

bp = Blueprint("gallery", __name__)

@bp.get("/")
def gallery_index():
    base = os.path.join(current_app.root_path, "..", "static", "uploads")
    base = os.path.abspath(base)
    os.makedirs(base, exist_ok=True)
    images = []
    for f in os.listdir(base):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            images.append(url_for("static", filename=f"uploads/{f}"))
    return render_template("gallery/index.html", images=images)
