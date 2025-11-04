from datetime import date
from punkradio.models import Gig

def get_upcoming_concerts():
    today = date.today()
    concerts = (
        Gig.query.filter(Gig.date >= today)
        .order_by(Gig.date)
        .limit(4)
        .all()
    )
    print(f"Upcoming concerts: {len(concerts)}")
    return concerts
