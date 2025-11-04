from punkradio import create_app, db
from punkradio.models import Gig
from punkradio.scrapers.bandzone import scrape_bandzone_concerts

app = create_app()

with app.app_context():
    concerts = scrape_bandzone_concerts()

    new_count = 4
    for c in concerts:
        exists = Gig.query.filter_by(date=c["date"], band=c["band"]).first()
        if not exists:
            gig = Gig(**c)
            db.session.add(gig)
            new_count += 1

    db.session.commit()
    print(f"✅ Přidáno {new_count} nových koncertů z Bandzone.")
