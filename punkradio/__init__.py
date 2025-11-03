from flask import Flask
from .config import Config
from .extensions import db, migrate, csrf




def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # blueprints
    from punkradio.blueprints.main.routes import bp as main_bp
    from punkradio.blueprints.bands.routes import bp as bands_bp
    from punkradio.blueprints.gigs.routes import bp as gigs_bp
    from punkradio.blueprints.news.routes import bp as news_bp
    from punkradio.blueprints.gallery.routes import bp as gallery_bp
    from punkradio.blueprints.komunita import bp as komunita_bp
    from punkradio.blueprints.Kontakt import bp as kontakt_bp
    
    
    app.register_blueprint(kontakt_bp)  
    app.register_blueprint(komunita_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(bands_bp, url_prefix="/kapely")
    app.register_blueprint(gigs_bp, url_prefix="/koncerty")
    app.register_blueprint(news_bp, url_prefix="/novinky")
    app.register_blueprint(gallery_bp, url_prefix="/galerie")

    # context: today.year do patičky
    from datetime import date
    @app.context_processor
    def inject_today():
        return {"today": date.today()}

    return app
