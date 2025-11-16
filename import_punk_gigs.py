import json
import os
from datetime import datetime
from punkradio import create_app, db
from punkradio.models import Gig

# 🧭 Cesty k souborům
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "filtered", "punk_events.json")

# 🧩 Vytvoření Flask app contextu
app = create_app()
app.app_context().push()

# 🔍 Načtení dat
if not os.path.exists(JSON_PATH):
    raise FileNotFoundError(f"Soubor {JSON_PATH} nebyl nalezen!")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

punk_events = data.get("punk_rock_events", [])
print(f"📥 Načteno {len(punk_events)} punk koncertů ze souboru.\n")

# 💾 Uložení do DB
count = 0
for ev in punk_events:
    try:
        date_str = ev.get("date") or None
        event_date = None
        if date_str:
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                event_date = None

        gig = Gig(
            date=event_date or datetime.utcnow().date(),
            city=ev.get("city") or "",
            venue=(ev.get("venue") or {}).get("name", "") if isinstance(ev.get("venue"), dict) else ev.get("venue", ""),
            lineup=[ev.get("name")] if ev.get("name") else [],
        )

        db.session.add(gig)
        count += 1

        if count % 50 == 0:
            print(f"💿 Uloženo {count} koncertů...")

    except Exception as e:
        print(f"⚠️ Chyba při ukládání eventu: {e}")

# 🔐 Commit
db.session.commit()

print(f"\n✅ Import dokončen! Uloženo {count} koncertů do databáze instance/app.db.")
print("💥 Zkontroluj je na webu v sekci /gigs.")
