import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "..", "instance", "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False



    # volitelné e-mail notifikace pro přihlášky kapel
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASS = os.getenv("SMTP_PASS", "")
