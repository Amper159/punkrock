import os
import re
import json
from datetime import datetime
from punkradio.models import Gig, db
from punkradio import create_app

# 🧠 Inicializace Flask aplikace
app = create_app()

with app.app_context():
    # 📂 Cesta k JSONu s punk koncerty
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "filtered", "punk_events.json")

    if not os.path.exists(file_path):
        print(f"❌ Soubor {file_path} nebyl nalezen!")
        exit(1)

    # 📖 Načtení JSONu
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        gigs = data.get("punk_rock_events", [])

    if not gigs:
        print("⚠️ Žádné koncerty k importu (soubor je prázdný nebo neplatný).")
        exit(0)

    # 🧹 Vymazání starých záznamů
    print("🧽 Mažu staré koncerty...")
    Gig.query.delete()
    db.session.commit()

    print(f"🎸 Načítám {len(gigs)} koncertů z JSONu...")

    # 📚 Seznam známých klubů a měst
    known_venues = [
        # Praha
        "rock café", "vagon", "roxy", "cross club", "futurum", "klub 007 strahov", "strahov 007",
        "storm club", "klub fatal", "underdogs", "radost fx", "klub radost", "chapeau rouge",
        "modrá vopice", "lucerna", "kaštan", "klubovna", "meetfactory", "mlejn", "cargo gallery",

        # Brno
        "fléda", "melodka", "kabinet múz", "metro music bar", "první patro", "music lab",
        "sono centrum", "stará pekárna", "rusty nail", "brooklyn bar",

        # Ostrava
        "barrák", "brickhouse", "plato", "fabric", "cooltour", "plan b", "heligonka",

        # Plzeň
        "divadlo pod lampou", "watt club", "anděl café", "zach's pub", "house of blues",

        # Olomouc
        "s klub", "u klub", "bounty rock café", "letní kino", "uc klub",

        # Hradec / Pardubice
        "náplavka", "čp 4", "zkušebna pardubice", "zahrádka hradec", "music bar hoblina",

        # Liberec / Jablonec
        "bedna", "klub na rampě", "beseda jablonec", "klub čarák",

        # Jižní Morava
        "m13 rock hell", "klub beat", "klub radnice", "kd kyjov", "music club podhodou",

        # Ostatní
        "klub", "kulturní dům", "kino", "pub", "bar", "rock klub", "music club", "underground"
    ]

    known_cities = [
        "praha", "brno", "ostrava", "plzeň", "olomouc", "hradec králové", "pardubice",
        "liberec", "zlín", "kladno", "teplice", "jihlava", "tábor", "písek", "cheb",
        "šumperk", "opava", "trutnov", "přerov", "třebíč", "frýdek-místek", "břeclav"
    ]

    imported = 0

    for event in gigs:
        # 🗓️ Datum
        date_str = event.get("date")
        date_obj = None
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                date_obj = datetime.utcnow().date()

        # 🏙️ Město
        city = event.get("city", "").strip().lower()
        if not city or city == "neznámé město":
            # zkus najít město v URL nebo popisu
            combined_text = (event.get("booking_url", "") + " " + event.get("description", "")).lower()
            for c in known_cities:
                if c in combined_text:
                    city = c
                    break
        if not city:
            city = "neznámé město"

        # 🎸 Klub
        venue_name = event.get("venue", "").strip().lower()
        if not venue_name or venue_name == "neznámý klub":
            combined_text = (event.get("booking_url", "") + " " + event.get("description", "")).lower()
            for v in known_venues:
                if v in combined_text:
                    venue_name = v
                    break
        if not venue_name:
            venue_name = "neznámý klub"

        # 💾 Vytvoření nového záznamu
        new_gig = Gig(
            date=date_obj,
            city=city.title(),
            venue=venue_name.title(),
            lineup=[event.get("name")] if event.get("name") else [],
        )

        db.session.add(new_gig)
        imported += 1

    db.session.commit()

    print(f"\n✅ Import hotov! Do databáze bylo přidáno {imported} koncertů.")
    print(f"📅 Data pochází ze souboru: {file_path}")
