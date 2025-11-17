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
    published_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
