import os
import json
import ijson
from typing import List, Dict, Any


class PunkRockFilter:
    """Filtruje punkové koncerty z JSONu smsticket_rock_events.json"""

    def __init__(self, input_file: str, output_file: str):
        self.input_file = input_file
        self.output_file = output_file
        self.total_events = 0
        self.punk_events = 0
        self.punk_keywords = [
            "punk", "punk rock", "punkrock", "hardcore punk",
            "pop punk", "ska punk", "street punk", "anarcho punk"
        ]

    # -------------------------------------------
    # Extrakce dat
    # -------------------------------------------

    def extract_genres(self, event: Dict[str, Any]) -> List[str]:
        """Získá žánry z eventu (pokud existují)"""
        genres = []
        try:
            classification = event.get("classfication", event.get("classification", {}))
            themes = classification.get("themes", {})
            theme_list = themes.get("theme", [])
            if isinstance(theme_list, dict):
                theme_list = [theme_list]

            for theme in theme_list:
                if isinstance(theme, dict):
                    genre_data = theme.get("genres", {}).get("genre", [])
                    if isinstance(genre_data, str):
                        genres.append(genre_data.lower())
                    elif isinstance(genre_data, list):
                        genres.extend([g.lower() for g in genre_data if isinstance(g, str)])
        except Exception:
            pass
        return genres

    def extract_theme_names(self, event: Dict[str, Any]) -> List[str]:
        """Získá názvy témat"""
        names = []
        try:
            classification = event.get("classfication", event.get("classification", {}))
            themes = classification.get("themes", {})
            theme_list = themes.get("theme", [])
            if isinstance(theme_list, dict):
                theme_list = [theme_list]
            for theme in theme_list:
                if isinstance(theme, dict):
                    name = theme.get("name")
                    if name:
                        names.append(name)
        except Exception:
            pass
        return names

    # -------------------------------------------
    # Logika filtrování
    # -------------------------------------------

    def is_punk_event(self, event: Dict[str, Any]) -> bool:
        """Vrátí True, pokud event obsahuje 'punk' v žánrech, typech nebo popisu"""
        text_fields = []

        # Žánry
        genres = self.extract_genres(event)
        text_fields.extend(genres)

        # Typ (např. Koncert)
        types = event.get("types", {}).get("type", [])
        if isinstance(types, str):
            types = [types]
        text_fields.extend(types)

        # Popis
        description = (event.get("description") or "").lower()
        text_fields.append(description)

        # Kontrola klíčových slov
        for text in text_fields:
            for keyword in self.punk_keywords:
                if keyword in text.lower():
                    return True
        return False

    # -------------------------------------------
    # Zpracování dat
    # -------------------------------------------

    def process_events(self):
        """Načte JSON a uloží pouze punkrockové koncerty"""
        print("🎸 Načítám data a filtruji punkrockové koncerty...\n")
        os.makedirs(os.path.dirname(self.output_file) or ".", exist_ok=True)

        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Soubor '{self.input_file}' nebyl nalezen!")

        with open(self.input_file, "r", encoding="utf-8") as infile, \
             open(self.output_file, "w", encoding="utf-8") as outfile:

            outfile.write('{"punk_rock_events": [\n')
            first = True

            for event in ijson.items(infile, "rock_events.item"):
                self.total_events += 1

                if self.is_punk_event(event):
                    self.punk_events += 1
                    if not first:
                        outfile.write(",\n")
                    else:
                        first = False

                    json.dump({
                        "booking_url": event.get("booking_url", ""),
                        "name": event.get("name", ""),
                        "description": event.get("description", ""),
                        "types": event.get("types", {}).get("type", ""),
                        "genres": self.extract_genres(event),
                        "themes": self.extract_theme_names(event),
                        "date": event.get("dates", {}).get("start_date", ""),
                        "city": (
                        event.get("city")
                        or event.get("city_name")
                        or event.get("place", {}).get("city")
                        or event.get("venue", {}).get("city")
                        or event.get("location", {}).get("city")
                        or ""
                        ),
                        "venue": (
                            event.get("venue")
                            or event.get("venue_name")
                            or event.get("place", {}).get("name")
                            or event.get("location", {}).get("venue")
                            or ""
                        )

                    }, outfile, ensure_ascii=False, indent=2)

                if self.total_events % 2000 == 0:
                    print(f"Zpracováno {self.total_events} eventů...")

            outfile.write("\n  ],\n")
            outfile.write(f'  "total_count": {self.punk_events}\n}}\n')


        print(f"\n✅ Hotovo! Načteno {self.total_events} eventů, nalezeno {self.punk_events} punkrockových.")
        print(f"💾 Výsledky uloženy do: {self.output_file}")

    # -------------------------------------------
    # Shrnutí
    # -------------------------------------------

    def print_summary(self, limit: int = 10):
        """Vypíše přehled nalezených koncertů"""
        with open(self.output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            punk_events = data.get("punk_rock_events", [])
            print(f"\n=== SHRNUTÍ ===")
            print(f"Celkem punkrockových koncertů: {len(punk_events)}")
            for i, event in enumerate(punk_events[:limit], 1):
                print(f"\n{i}. {event.get('name', 'Neznámý název')}")
                print(f"   URL: {event.get('booking_url', 'Bez odkazu')}")
                print(f"   Datum: {event.get('date', '')}")
                print(f"   Typ: {event.get('types', '')}")
                print(f"   Popis: {event.get('description', '')[:120]}...")
            if len(punk_events) > limit:
                print(f"\n(Zobrazeno prvních {limit} z {len(punk_events)})")


# 🚀 ---- Hlavní spuštění ----

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(BASE_DIR, "smsticket_rock_events.json")
    output_file = os.path.join(BASE_DIR, "..", "filtered", "punk_events.json")

    print(f"📂 Vstupní soubor: {input_file}")
    print(f"📂 Výstupní soubor: {output_file}")

    filterer = PunkRockFilter(input_file, output_file)
    filterer.process_events()
    filterer.print_summary()


if __name__ == "__main__":
    main()
