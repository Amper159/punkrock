from datetime import datetime, date
from .extensions import db

class Band(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(80))
    styles = db.Column(db.String(200))      # CSV "punk, hardcore"
    about = db.Column(db.Text)
    links = db.Column(db.JSON)
    is_approved = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Gig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, nullable=False)
    city = db.Column(db.String(80))
    venue = db.Column(db.String(120))
    lineup = db.Column(db.JSON)             # ["Kapela A", "Kapela B"]
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    source = db.Column(db.String(40))                       # "manual" / "smsticket"
    external_id = db.Column(db.String(120), unique=True, index=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(160), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    band = db.Column(db.String(120))
    perex = db.Column(db.String(500)) 
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    body = db.Column(db.Text)
    tags = db.Column(db.JSON)
    source_url = db.Column(db.String(500))    # externí odkaz na plný článek (curated link-out)
    source_name = db.Column(db.String(120))   # název zdroje, např. "insounder.org"
    published_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(20), nullable=False, index=True)  # "gig" | "article"
    target_id = db.Column(db.Integer, nullable=False, index=True)
    author_name = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, index=True)  # rovnou vidět, moderace zpětně přes CLI
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class GigPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(db.Integer, db.ForeignKey("gig.id"), nullable=True, index=True)
    uploader_name = db.Column(db.String(80), nullable=False)
    caption = db.Column(db.String(200))
    filename = db.Column(db.String(255), nullable=False)
    is_approved = db.Column(db.Boolean, default=False, index=True)  # fotky se schvalují předem
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    gig = db.relationship("Gig", backref="photos")
