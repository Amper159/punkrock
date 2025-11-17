import os
import sys
from datetime import datetime
from slugify import slugify  # pip install python-slugify

# 🧭 Umožní import modulu punkradio i při spouštění zvenku
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from punkradio.models import Article, db
from punkradio import create_app

# 🧠 Inicializace Flask aplikace
app = create_app()

with app.app_context():
    print("📰 Spouštím seed skript pro novinky...")

    # 🧹 Smažeme existující články, aby se neduplikovaly
    Article.query.delete()
    db.session.commit()

    # 🧾 Seznam článků
    articles = [
        Article(
            slug=slugify("Plexisovjanka oznamuje zimní tour 2025"),
            title="Plexisovjanka oznamuje zimní tour 2025",
            band="Plexisovjanka",
            perex="Legendární Plexisovjanka vyráží na zimní tour po celé republice. Oslaví 40 let od založení kapely Plexis.",
            content="""
                <p>Kapela <strong>Plexisovjanka</strong>, která vznikla jako pocta legendárnímu frontmanovi 
                <strong>Petrovi Hoškovi</strong>, oznámila sérii koncertů po celé České republice. 
                Turné startuje 27. listopadu v pražském <em>Rock Café</em> a pokračuje přes Brno, Ostravu i Hradec Králové.</p>
                <p>"Chceme fanouškům připomenout, že punk je pořád naživu," říká baskytarista <strong>Eda Fröhlich</strong>.</p>
            """,
            excerpt="Plexisovjanka startuje tour na počest Petra Hoška.",
            tags=["punk", "tour", "Plexis"],
            published_at=datetime(2025, 11, 10, 18, 0)
        ),
        Article(
            slug=slugify("Just-War chystají nový singl"),
            title="Just Wär chystají nový singl",
            band="Just Wär",
            perex="Pražská punk'n'rollová kapela Just Wär ohlásila nový singl s názvem 'Prach a krev'.",
            content="""
                <p><strong>Just Wär</strong> potvrdili vydání nového singlu <em>Prach a krev</em>, který má vyjít v prosinci 2025. 
                Song vznikl ve spolupráci s producentem z berlínského labelu Dirty Sound Records a navazuje na 
                energický styl známý z jejich předchozí desky <em>Situation Normal Still Fucked Up</em>.</p>
                <p>K singlu kapela plánuje i videoklip natáčený v žižkovských barech. 
                "Bude to upřímné, špinavé a poctivé – přesně tak, jak má punk vypadat," dodává zpěvák Brian.</p>
            """,
            excerpt="Nový singl Just Wär vyjde už v prosinci!",
            tags=["punk", "nový singl", "Praha"],
            published_at=datetime(2025, 11, 8, 15, 0)
        ),
        Article(
            slug=slugify("Festival Pod Parou potvrzuje první jména 2026"),
            title="Festival Pod Parou potvrzuje první jména 2026",
            band=None,
            perex="Největší punkový festival v Česku odhalil první kapely pro ročník 2026. Vrátí se Cock Sparrer i Slobodná Európa!",
            content="""
                <p>Organizátoři legendárního festivalu <strong>Pod Parou</strong> oznámili první kapely pro rok 2026. 
                Na pódiu se objeví mimo jiné <em>Cock Sparrer</em>, <em>Slobodná Európa</em> a české 
                kapely <strong>The Fialky</strong> a <strong>Nežfaleš</strong>.</p>
                <p>Festival se tradičně koná ve <em>Vyškově</em> a proběhne 7.–9. srpna 2026. 
                Vstupenky jsou už v předprodeji na oficiálním webu akce.</p>
            """,
            excerpt="Festival Pod Parou 2026: první jména potvrzena!",
            tags=["festival", "punk", "Pod Parou"],
            published_at=datetime(2025, 11, 12, 12, 0)
        ),
        Article(
            slug=slugify("Znouzectnost vydává nové album"),
            title="Znouzectnost vydává nové album",
            band="Znouzectnost",
            perex="Plzeňská legenda Znouzectnost se vrací s novým albem 'Návrat z podzemí'.",
            content="""
                <p><strong>Znouzectnost</strong> po čtyřech letech vydává nové studiové album s názvem <em>Návrat z podzemí</em>. 
                Deska obsahuje 11 skladeb, které kombinují klasický český punk s poetickými texty 
                a melancholickou energií, která je pro kapelu typická.</p>
                <p>Album vychází 20. listopadu 2025 a křest proběhne v plzeňském klubu <em>Anděl Café</em>.</p>
            """,
            excerpt="Nové album Znouzectnosti vychází už 20. listopadu!",
            tags=["punk", "album", "Plzeň"],
            published_at=datetime(2025, 11, 11, 20, 0)
        ),
    ]

    # 💾 Uložení do databáze
    db.session.add_all(articles)
    db.session.commit()

    print(f"✅ Do databáze bylo přidáno {len(articles)} článků.")
    print("📰 Novinky jsou připravené k zobrazení na webu.")
