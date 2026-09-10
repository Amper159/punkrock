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
import unicodedata
from datetime import datetime

import click
import requests
import xmltodict
from flask import current_app
from flask.cli import with_appcontext

from .extensions import db
from .models import Gig, Article

SMSTICKET_API_URL = "https://www.smsticket.cz/api/public/v1.1/events"

DEFAULT_KEYWORDS = [
    "punk", "hardcore", "oldschool", "street punk", "streetpunk",
    "ska", "grunge", "pop punk", "poppunk",
]


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def _matches_keywords(event: dict, keywords: list[str]) -> bool:
    haystack = " ".join(
        str(event.get(field, "") or "")
        for field in ("name", "description", "genre", "category")
    ).lower()
    return any(kw in haystack for kw in keywords)


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

    raw_date = event.get("date") or event.get("date_from") or event.get("dateFrom")
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
    place = event.get("place") or event.get("venue")
    if isinstance(place, dict):
        venue = place.get("name") or place.get("venue")
        city = place.get("city") or place.get("town")
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
    }


@click.command("sync-gigs")
@click.option("--dry-run", is_flag=True, help="Jen stáhne a vypíše první event, nic neukládá do DB.")
@click.option("--keywords", default=None, help="Čárkou oddělený seznam klíčových slov (přepíše výchozí).")
@with_appcontext
def sync_gigs_command(dry_run, keywords):
    """Stáhne akce ze SMSticket.cz a uloží ty, co odpovídají žánru."""
    kw_list = [k.strip().lower() for k in keywords.split(",")] if keywords else DEFAULT_KEYWORDS

    click.echo(f"Stahuji {SMSTICKET_API_URL} ...")
    try:
        resp = requests.get(SMSTICKET_API_URL, timeout=30)
        resp.raise_for_status()
        data = xmltodict.parse(resp.content)
    except requests.exceptions.RequestException as e:
        click.echo(f"Chyba při stahování: {e}", err=True)
        return

    events = data.get("events", {}).get("event", [])
    if isinstance(events, dict):
        events = [events]
    click.echo(f"Staženo {len(events)} akcí celkem.")

    if dry_run:
        click.echo("--- DRY RUN: syrová struktura prvního eventu ---")
        click.echo(json.dumps(events[0] if events else {}, indent=2, ensure_ascii=False))
        click.echo("--- konec dry-run, nic se neuložilo ---")
        return

    matched = [e for e in events if _matches_keywords(e, kw_list)]
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


def register_cli(app):
    app.cli.add_command(sync_gigs_command)
    app.cli.add_command(add_news_command)
