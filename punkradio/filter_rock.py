import requests
import xmltodict
import json

def get_rock_events_from_smsticket():
    """
    Stáhne XML data z SMSticket API, převede je na Python slovník 
    a vyfiltruje rockové a metalové události.
    """
    url = "https://www.smsticket.cz/api/public/v1.1/events"
    print("📥 Stahuji a parsuji data z SMSticket API...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Převedení XML na Python slovník
        data = xmltodict.parse(response.content)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Chyba při stahování dat. Ujistěte se, že API URL je správné a klíč není potřeba: {e}")
        return []

    # Zde předpokládáme, že struktura je podobná: root -> events -> event
    events_list = data.get('events', {}).get('event', [])
    if not isinstance(events_list, list):
         # Může se stát, že pro 1 událost vrací slovník, ne seznam
        events_list = [events_list]
        
    print(f"Celkem nalezeno událostí: {len(events_list)}")
    
    # Klíčová slova pro filtrování
    rock_keywords = ["rock", "metal", "punk", "hardcore", "alternative", "ska", "grunge"]
    
    filtered_events = []
    
    # 🔎 FILTROVÁNÍ
    for event in events_list:
        # Převedeme všechny relevantní textové pole na malá písmena pro jednoduché porovnání
        
        # Získání hodnot z eventu (s ošetřením, že nemusí existovat)
        name = event.get('name', '')
        description = event.get('description', '')
        genre = event.get('genre', '')# Použijte název pole pro žánr, pokud je k dispozici
        
        is_rock = False
        
        # Kontrola, zda se klíčové slovo nachází v názvu, popisu nebo žánru
        for keyword in rock_keywords:
            if keyword in name or keyword in description or keyword in genre:
                is_rock = True
                break
        
        if is_rock:
            filtered_events.append(event)
    
    print(f"✅ Vyfiltrováno rockových událostí: {len(filtered_events)}")
    return filtered_events

# --- Spuštění ---
if __name__ == '__main__':
    rock_data = get_rock_events_from_smsticket()
    
    if rock_data:
        # Vytvoření finálního JSON objektu s filtrovanými daty
        final_json = json.dumps({"rock_events": rock_data}, indent=4, ensure_ascii=False)
        
        # Uložení do souboru pro snadné nahrání na Váš web
        with open("smsticket_rock_events.json", "w", encoding="utf-8") as f:
            f.write(final_json)
            
        print("\n💾 Filtrované rockové události byly uloženy do souboru: **smsticket_rock_events.json**")
        print("\n--- Náhled první události ---")
        print(json.dumps(rock_data[0], indent=4, ensure_ascii=False))