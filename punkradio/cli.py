"""
Flask CLI příkazy pro naplnění webu reálným obsahem.

    flask sync-gigs [--dry-run] [--keywords punk,hardcore,...]
        Stáhne aktuální akce z veřejného API SMSticket.cz a uloží ty,
        co odpovídají žánrovým klíčovým slovům, jako Gig záznamy.
        Bezpečné spouštět opakovaně (cron) — dedupe přes external_id.

    flask add-news "Titul" "https://zdroj.example/clanek" \
        --source "insounder.org" --perex "Krátký popisek" --band "Plexis"
        Přidá curated novinku typu link-out — na webu se zobrazí jen
        titulek + krátký perex napsaný vámi a odkaz na originál.
        Text článku se NIKAM nekopíruje.

Poznámka k SMSticket API:
    Pole v jejich XML feedu (název, datum, místo, žánr...) jsem si ověřil
    jen z veřejné dokumentace a ukázek, ne z živého volání (sandbox, ve
    kterém tenhle kód vznikl, nemá k smsticket.cz síťový přístup).
    Při prvním spuštění PROTO nejdřív spusťte:

        flask sync-gigs --dry-run

    a zkontrolujte v konzoli vypsaný syrový XML->dict výstup prvního
    eventu. Pokud se názvy klíčů (name/date/venue/city/genre...) liší,
    uprav si je v _parse_event() níže — je to jedno malé místo v kódu.
"""
import re
import json
import os
import unicodedata
from datetime import datetime

import click
import requests
import xmltodict
from flask import current_app
from flask.cli import with_appcontext

from .extensions import db
from .models import Gig, Article, Band, Comment, GigPhoto

SMSTICKET_API_URL = "https://www.smsticket.cz/api/public/v1.1/events"

DEFAULT_KEYWORDS = [
    "punk", "hardcore", "oldschool", "streetpunk", "ska",
    "grunge", "poppunk",
]

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(value: str) -> str:
    return _TAG_RE.sub(" ", value or "")


def _keyword_pattern(keywords: list[str]) -> "re.Pattern":
    # Krátká slova jako "ska" musí sedět jako celé slovo (jinak chytnou
    # "riskantní", "skautský" apod.). Delší klíčová slova (punk, hardcore...)
    # smí mít za sebou další písmena, aby chytla i česká skloňování a
    # složeniny (punkrock, punková, hardcorový, poppunkový...), ale ne
    # PŘED sebou — takže "expunk" by nešlo, ale "punkrockový" ano.
    parts = []
    for kw in keywords:
        kw = kw.strip().lower()
        if not kw:
            continue
        escaped = re.escape(kw)
        if len(kw.replace(" ", "")) <= 3:
            parts.append(rf"\b{escaped}\b")
        else:
            parts.append(rf"\b{escaped}\w*")
    return re.compile("|".join(parts), re.IGNORECASE) if parts else re.compile(r"(?!)")


def _matches_keywords(event: dict, pattern: "re.Pattern") -> bool:
    name = str(event.get("name", "") or "")
    description = _strip_html(str(event.get("description", "") or ""))
    haystack = f"{name} {description}"
    return bool(pattern.search(haystack))


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def _parse_event(event: dict):
    """
    Namapuje jeden event ze SMSticket XML na pole Gig modelu.

    NEOVĚŘENO PROTI ŽIVÉMU FEEDU — viz poznámka v docstringu modulu.
    Klíče níže vycházejí z původního filter_rock.py (name/description/genre
    jsou tam potvrzeně použité) a z veřejné dokumentace API pro zbytek.
    Po prvním --dry-run běhu tuhle funkci zkontroluj/uprav podle
    skutečné struktury.
    """
    external_id = event.get("id") or event.get("@id") or event.get("eventId")

    raw_date = None
    dates_obj = event.get("dates")
    if isinstance(dates_obj, dict):
        raw_date = dates_obj.get("start_date")
    raw_date = raw_date or event.get("date") or event.get("date_from") or event.get("dateFrom")

    event_date = None
    if raw_date:
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d.%m.%Y"):
            try:
                event_date = datetime.strptime(raw_date, fmt).date()
                break
            except (ValueError, TypeError):
                continue

    venue = None
    city = None
    latitude = None
    longitude = None
    place = event.get("place") or event.get("venue")
    if isinstance(place, dict):
        venue = place.get("company") or place.get("name") or place.get("venue")
        city = place.get("city") or place.get("town")
        wgs84 = place.get("wgs84")
        if isinstance(wgs84, dict):
            try:
                latitude = float(wgs84.get("latitude"))
                longitude = float(wgs84.get("longitude"))
            except (TypeError, ValueError):
                latitude = longitude = None
    elif isinstance(place, str):
        venue = place
    city = city or event.get("city") or event.get("town")

    name = event.get("name") or "Neznámá akce"

    return {
        "external_id": str(external_id) if external_id else None,
        "date": event_date,
        "city": city,
        "venue": venue,
        "lineup": [name],
        "latitude": latitude,
        "longitude": longitude,
    }


@click.command("sync-gigs")
@click.option("--dry-run", is_flag=True, help="Jen stáhne a vypíše první event, nic neukládá do DB.")
@click.option("--keywords", default=None, help="Čárkou oddělený seznam klíčových slov (přepíše výchozí).")
@click.option("--reset", is_flag=True, help="Před importem smaže všechny dřív naimportované smsticket koncerty (source='smsticket'). Ruční/manuální koncerty nechá být.")
@with_appcontext
def sync_gigs_command(dry_run, keywords, reset):
    """Stáhne akce ze SMSticket.cz a uloží ty, co odpovídají žánru."""
    kw_list = [k.strip().lower() for k in keywords.split(",")] if keywords else DEFAULT_KEYWORDS
    pattern = _keyword_pattern(kw_list)

    click.echo(f"Stahuji {SMSTICKET_API_URL} ...")
    try:
        resp = requests.get(SMSTICKET_API_URL, timeout=30)
        resp.raise_for_status()
        data = xmltodict.parse(resp.content)
    except requests.exceptions.RequestException as e:
        click.echo(f"Chyba při stahování: {e}", err=True)
        return

    events_root = data.get("events") or {}
    events = events_root.get("event", [])
    if isinstance(events, dict):
        events = [events]
    click.echo(f"Staženo {len(events)} akcí celkem.")

    if dry_run:
        sample = events[:5]
        click.echo(f"--- DRY RUN: přehled polí prvních {len(sample)} eventů ---")
        for i, ev in enumerate(sample):
            flat = {k: v for k, v in ev.items() if not isinstance(v, (dict, list))}
            nested = [k for k, v in ev.items() if isinstance(v, (dict, list))]
            if "description" in flat:
                flat["description"] = f"<{len(str(flat['description']))} znaků HTML>"
            matched = _matches_keywords(ev, pattern)
            click.echo(f"[event {i}] name={ev.get('name')!r}  MATCH={matched}")
            click.echo(f"  jednoduchá pole: {json.dumps(flat, ensure_ascii=False)}")
            click.echo(f"  vnořená pole:    {nested}")
            for nk in nested:
                if nk == "photos":
                    continue
                click.echo(f"    {nk} = {json.dumps(ev[nk], ensure_ascii=False)}")
        click.echo("--- konec dry-run, nic se neuložilo ---")
        return

    if reset:
        deleted = Gig.query.filter_by(source="smsticket").delete()
        db.session.commit()
        click.echo(f"--reset: smazáno {deleted} dřív naimportovaných smsticket koncertů.")

    matched = [e for e in events if _matches_keywords(e, pattern)]
    click.echo(f"Odpovídá klíčovým slovům {kw_list}: {len(matched)} akcí.")

    created, skipped = 0, 0
    for raw in matched:
        parsed = _parse_event(raw)
        if not parsed["date"]:
            skipped += 1
            continue

        if parsed["external_id"]:
            existing = Gig.query.filter_by(external_id=parsed["external_id"]).first()
            if existing:
                skipped += 1
                continue

        gig = Gig(
            date=parsed["date"],
            city=parsed["city"],
            venue=parsed["venue"],
            lineup=parsed["lineup"],
            latitude=parsed["latitude"],
            longitude=parsed["longitude"],
            source="smsticket",
            external_id=parsed["external_id"],
        )
        db.session.add(gig)
        created += 1

    db.session.commit()
    click.echo(f"Hotovo. Nově uloženo: {created}, přeskočeno (duplicita/chybí datum): {skipped}.")


@click.command("add-news")
@click.argument("title")
@click.argument("source_url")
@click.option("--source", "source_name", default=None, help="Název zdroje, např. insounder.org")
@click.option("--perex", default=None, help="Krátký vlastní popisek (nekopírovat text ze zdroje).")
@click.option("--band", default=None, help="Kapela, ke které se novinka váže.")
@with_appcontext
def add_news_command(title, source_url, source_name, perex, band):
    """Přidá curated novinku typu link-out (titulek + odkaz na originál)."""
    slug_base = _slugify(title)
    slug = slug_base
    i = 2
    while Article.query.filter_by(slug=slug).first():
        slug = f"{slug_base}-{i}"
        i += 1

    article = Article(
        slug=slug,
        title=title,
        band=band,
        perex=perex,
        content="",  # obsah se nekopíruje, viz source_url
        source_url=source_url,
        source_name=source_name,
        published_at=datetime.utcnow(),
    )
    db.session.add(article)
    db.session.commit()
    click.echo(f"Přidáno: {title}  ({slug}) -> {source_url}")


SEED_BANDS = [
    {
        "name": "Visací zámek",
        "city": "Praha",
        "styles": "punk, oldschool",
        "about": "Jedna z úplně prvních pražských punkových kapel, na scéně od roku 1982. Ikona české oldschool punkové scény.",
    },
    {
        "name": "Plexis",
        "city": "Praha",
        "styles": "punk rock",
        "about": "Pražská punková kapela vedená Petrem Hoškem, na scéně od 80. let.",
    },
    {
        "name": "Tři sestry",
        "city": "Praha",
        "styles": "punk rock, hardcore",
        "about": "Legendární kapela z branické hospody, na scéně od roku 1985. Frontman Lou Fanánek Hagen kapelu proslavil charakteristickým hlasem i texty.",
    },
    {
        "name": "Totální nasazení",
        "city": "Slaný",
        "styles": "street punk",
        "about": "Slánská parta, která už od roku 1990 šíří pozitivní energii a chytlavé punkrockové hymny s nadhledem i ironií.",
    },
    {
        "name": "The Fialky",
        "city": "Praha",
        "styles": "punk 77, street punk",
        "about": "Pražská kapela na scéně od roku 2000, hudebně navazující na první vlnu punku 77'. Patří mezi nejznámější současné české punkrockové kapely zpívající v češtině.",
    },
    {
        "name": "Tragedis",
        "city": "Jindřichův Hradec",
        "styles": "hardcore",
        "about": "Poctivý punkrock s ostrými riffy a přímočarými texty o životě, společnosti i vlastní cestě.",
    },
    {
        "name": "Vypsaná fixa",
        "city": "Pardubice",
        "styles": "pop punk, ska punk",
        "about": "Pardubická kapela založená v roce 1994, se zpěvákem Michalem Maredou. Jedna z nejposlouchanějších českých pop punkových kapel.",
    },
    {
        "name": "E!E",
        "city": "Příbram",
        "styles": "punk'n'roll",
        "about": "Příbramská punk'n'rollová kapela s dlouhou historií a nezaměnitelným syrovým zvukem.",
    },
    {
        "name": "Volant",
        "city": "Pardubice",
        "styles": "punk-power",
        "about": "Svižná pardubická punk-power kapela, pravidelný host na punkových festivalech po celé republice.",
    },
    {
        "name": "Glejt",
        "city": "Dubňany",
        "styles": "punk, hardcore",
        "about": "Kapela z Dubňan hrající rychlý, nekompromisní punk hraničící s hardcore.",
    },
    {
        "name": "Do řady!",
        "city": "Bílina / Teplice",
        "styles": "punk",
        "about": "Bílinsko-teplická formace na scéně téměř 40 let, i po tak dlouhé době stále aktivní a vydávající nové desky.",
    },
    {
        "name": "Zeměžluč",
        "city": None,
        "styles": "punk",
        "about": "Jedna z posledních stále fungujících československých punkových legend, v roce 2026 slaví 40 let na scéně.",
    },
    {
        "name": "Znouzectnost",
        "city": None,
        "styles": "folk punk",
        "about": "Kapela spojující punkovou energii s folkovou odnoží, stálice na českých open-air festivalech.",
    },
    {
        "name": "Nežfaleš",
        "city": None,
        "styles": "punk",
        "about": "Pravidelný host punkových open-air festivalů a benefičních akcí po celé republice.",
    },
    {
        "name": "Deratizéři",
        "city": "Slaný",
        "styles": "punk",
        "about": "Další kapela ze slánské punkové scény, často po boku Totálního nasazení.",
    },
    {
        "name": "Vision Days",
        "city": None,
        "styles": "punk, ska",
        "about": "Punkrock se srdcem i saxofonem — kombinace melodie a energie s prvky ska.",
    },
    {
        "name": "KT Bandits",
        "city": None,
        "styles": "punk, hardcore",
        "about": "Tvrdý punk-hardcore, pravidelně na sestavách větších punkových open-airů.",
    },
    {
        "name": "Švindl",
        "city": None,
        "styles": "punk rock",
        "about": "Kapela z okruhu punkrockových večírků a menších klubových akcí po celé republice.",
    },
    {
        "name": "Spray",
        "city": None,
        "styles": "punk",
        "about": "Kapela z československé punkové scény, v roce 2026 znovu oživila starou sestavu a vydala nahrávky z roku 1984.",
    },
    {
        "name": "Načo názov",
        "city": None,
        "styles": "punk",
        "about": "Slovenská punková kapela, pravidelně koncertující i na českých punkových akcích.",
    },
]


@click.command("seed-bands")
@with_appcontext
def seed_bands_command():
    """Jednorázově naplní stránku Kapely ověřeným seznamem českých/československých punkových kapel."""
    created, skipped = 0, 0
    for entry in SEED_BANDS:
        if Band.query.filter_by(name=entry["name"]).first():
            skipped += 1
            continue
        band = Band(
            name=entry["name"],
            city=entry["city"],
            styles=entry["styles"],
            about=entry["about"],
            is_approved=True,
        )
        db.session.add(band)
        created += 1
    db.session.commit()
    click.echo(f"Hotovo. Nově přidáno: {created}, přeskočeno (už existovaly): {skipped}.")


@click.command("pending")
@with_appcontext
def pending_command():
    """Vypíše vše, co čeká na schválení — kapely a fotky."""
    pending_bands = Band.query.filter_by(is_approved=False).order_by(Band.created_at.asc()).all()
    pending_photos = GigPhoto.query.filter_by(is_approved=False).order_by(GigPhoto.created_at.asc()).all()

    click.echo(f"=== Kapely čekající na schválení ({len(pending_bands)}) ===")
    for b in pending_bands:
        click.echo(f"  [{b.id}] {b.name} — {b.city or '?'} — schválit: flask approve-band {b.id}")

    click.echo(f"\n=== Fotky čekající na schválení ({len(pending_photos)}) ===")
    for p in pending_photos:
        gig_info = f"ke koncertu #{p.gig_id}" if p.gig_id else "bez přiřazení"
        click.echo(f"  [{p.id}] od {p.uploader_name} ({gig_info}) — {p.filename}")
        click.echo(f"        schválit: flask approve-photo {p.id}  |  zamítnout: flask reject-photo {p.id}")

    if not pending_bands and not pending_photos:
        click.echo("Nic nečeká na schválení. 🤘")


@click.command("approve-band")
@click.argument("band_id", type=int)
@with_appcontext
def approve_band_command(band_id):
    """Schválí kapelu přihlášenou přes formulář — objeví se na /kapely/."""
    band = Band.query.get(band_id)
    if not band:
        click.echo(f"Kapela #{band_id} neexistuje.", err=True)
        return
    band.is_approved = True
    db.session.commit()
    click.echo(f"Schváleno: {band.name}")


@click.command("approve-photo")
@click.argument("photo_id", type=int)
@with_appcontext
def approve_photo_command(photo_id):
    """Schválí fotku — objeví se v galerii na /fotky/."""
    photo = GigPhoto.query.get(photo_id)
    if not photo:
        click.echo(f"Fotka #{photo_id} neexistuje.", err=True)
        return
    photo.is_approved = True
    db.session.commit()
    click.echo(f"Schváleno: fotka #{photo.id} od {photo.uploader_name}")


@click.command("reject-photo")
@click.argument("photo_id", type=int)
@with_appcontext
def reject_photo_command(photo_id):
    """Zamítne a smaže fotku (i soubor z disku)."""
    photo = GigPhoto.query.get(photo_id)
    if not photo:
        click.echo(f"Fotka #{photo_id} neexistuje.", err=True)
        return
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], photo.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(photo)
    db.session.commit()
    click.echo(f"Smazáno: fotka #{photo_id}")


@click.command("delete-comment")
@click.argument("comment_id", type=int)
@with_appcontext
def delete_comment_command(comment_id):
    """Smaže komentář (např. spam nebo nevhodný obsah)."""
    comment = Comment.query.get(comment_id)
    if not comment:
        click.echo(f"Komentář #{comment_id} neexistuje.", err=True)
        return
    db.session.delete(comment)
    db.session.commit()
    click.echo(f"Smazáno: komentář #{comment_id} od {comment.author_name}")


def register_cli(app):
    app.cli.add_command(sync_gigs_command)
    app.cli.add_command(add_news_command)
    app.cli.add_command(seed_bands_command)
    app.cli.add_command(pending_command)
    app.cli.add_command(approve_band_command)
    app.cli.add_command(approve_photo_command)
    app.cli.add_command(reject_photo_command)
    app.cli.add_command(delete_comment_command)
