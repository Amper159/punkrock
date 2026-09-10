from datetime import date, timedelta
from collections import defaultdict
from flask import Blueprint, render_template, abort, Response
from punkradio.models import Gig, Comment
from punkradio.forms import CommentForm


bp = Blueprint("gigs", __name__, url_prefix="/koncerty")

@bp.route("/")
def gigs_list():
    today = date.today()

    # 🎸 Jen budoucí koncerty, seřazené podle data
    gigs = (
        Gig.query
        .filter(Gig.date >= today)
        .order_by(Gig.date.asc())
        .all()
    )

    map_gigs = [
        {
            "lat": g.latitude,
            "lng": g.longitude,
            "name": ", ".join(g.lineup) if g.lineup else "Neznámá kapela",
            "venue": g.venue or "",
            "city": g.city or "",
            "date": g.date.strftime("%d.%m.%Y"),
            "id": g.id,
        }
        for g in gigs
        if g.latitude is not None and g.longitude is not None
    ]

    comments_by_gig = defaultdict(list)
    if gigs:
        gig_ids = [g.id for g in gigs]
        rows = (
            Comment.query
            .filter(Comment.target_type == "gig", Comment.target_id.in_(gig_ids), Comment.is_approved == True)
            .order_by(Comment.created_at.asc())
            .all()
        )
        for c in rows:
            comments_by_gig[c.target_id].append(c)

    comment_form = CommentForm()

    return render_template(
        "gigs/koncerty.html",
        gigs=gigs, today=today, map_gigs=map_gigs,
        comments_by_gig=comments_by_gig, comment_form=comment_form,
    )


def _ics_escape(value: str) -> str:
    return (value or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


@bp.route("/<int:gig_id>.ics")
def gig_ics(gig_id):
    gig = Gig.query.get(gig_id)
    if not gig:
        abort(404)

    summary = ", ".join(gig.lineup) if gig.lineup else "Punkový koncert"
    location_parts = [p for p in [gig.venue, gig.city] if p]
    location = ", ".join(location_parts)

    dtstart = gig.date.strftime("%Y%m%d")
    dtend = (gig.date + timedelta(days=1)).strftime("%Y%m%d")
    dtstamp = date.today().strftime("%Y%m%dT000000Z")
    uid = f"gig-{gig.id}@punk77.cz"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Punkrock 77//koncerty//CS",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;VALUE=DATE:{dtstart}",
        f"DTEND;VALUE=DATE:{dtend}",
        f"SUMMARY:{_ics_escape(summary)}",
        f"LOCATION:{_ics_escape(location)}",
        f"DESCRIPTION:{_ics_escape('Koncert na Punkrock 77 — ' + summary)}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    body = "\r\n".join(lines) + "\r\n"

    return Response(
        body,
        mimetype="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=koncert-{gig.id}.ics"},
    )
