import requests
from bs4 import BeautifulSoup
from datetime import datetime


def scrape_bandzone_concerts(limit=10):
    url = "https://www.bandzone.cz/koncerty"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")  # Assign the result to the soup variable

    concerts = []

    rows = soup.select("div.calendarItem")[:limit]
    for row in rows:
        try:
            date_text = row.select_one("div.calendarDate").get_text(strip=True)
            date = datetime.strptime(date_text, "%d.%m.%Y")
            city = row.select_one("div.calendarCity").get_text(strip=True)
            venue = row.select_one("div.calendarVenue").get_text(strip=True)
            band = row.select_one("div.calendarBand").get_text(strip=True)

            concerts.append({
                "band": band,
                "city": city,
                "venue": venue,
                "date": date.date()
            })
        except Exception as e:
            print("❌ Chyba při čtení záznamu:", e)

    return concerts