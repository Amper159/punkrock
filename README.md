```markdown
# punkrock

Krátký popis
: punkrock je lehká Python aplikace (web + šablony), která používá Mako/HTML pro front-end a Python pro backend. Tento repozitář obsahuje zdrojový kód, šablony a doprovodné nástroje pro vývoj a nasazení.

Badges
- build / tests / coverage / lint — přidejte dle CI (GitHub Actions)
- license — přidejte dle LICENSE souboru

Hlavní technologie
- Python (≈60%)
- HTML (≈38%)
- Mako (≈2%)

Funkce
- Rychlá webová aplikace s Mako šablonami
- Jednoduché routování / API (popis konkrétních endpointů doplňte)
- Konfigurovatelné prostředí přes environment proměnné
- Testy a linting (doporučeno)

Rychlý start (lokálně)
1. Klonovat repo
   ```
   git clone https://github.com/Amper159/punkrock.git
   cd punkrock
   ```

2. Vytvořit virtuální prostředí a nainstalovat závislosti
   ```
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -U pip
   pip install -r requirements.txt
   # nebo pokud používáte pyproject.toml / poetry:
   # pip install ".[dev]"  nebo  poetry install
   ```

3. Spuštění aplikace (přizpůsobte podle frameworku)
   - Pokud je to jednoduchý modul:
     ```
     python -m punkrock
     ```
   - Pokud používáte Flask:
     ```
     export FLASK_APP=punkrock
     export FLASK_ENV=development
     flask run
     ```
   - Nebo přes gunicorn:
     ```
     gunicorn punkrock:app
     ```

