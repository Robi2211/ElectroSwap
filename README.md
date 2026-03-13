# ElectroSwap

ElectroSwap ist eine Flask-basierte E-Commerce-Plattform für Elektronikgeräte (Laptops, Smartphones, Tablets, Audio-Geräte). Die Daten werden in MongoDB gespeichert.

## Projekt starten

```bash
pip install -r requirements.txt
python run.py          # App starten
python seed_data.py    # Beispieldaten einfügen
python -m pytest tests/ -v  # Tests ausführen
```

---

## Hauptentitätsmenge: `Product` (Produkt)

Die **Hauptentität** des Projekts ist `Product` (definiert in `app/models/product.py`).  
Sie besitzt **12 Attribute**, davon **8 Pflichtfelder** – damit ist Lernziel 2.4 (≥ 8 Attribute) erfüllt.

| # | Attribut | Typ | Pflicht | Beschreibung |
|---|----------|-----|:-------:|--------------|
| 1 | `name` | `str` | ✅ | Name des Produkts (z. B. „Apple MacBook Pro 14"") |
| 2 | `description` | `str` | ✅ | Ausführliche Produktbeschreibung |
| 3 | `price` | `float` | ✅ | Verkaufspreis in Euro (≥ 0) |
| 4 | `category` | `str` | ✅ | Produktkategorie (z. B. „Laptops", „Smartphones", „Tablets", „Audio") |
| 5 | `brand` | `str` | ✅ | Marke / Hersteller (z. B. „Apple", „Samsung", „Sony") |
| 6 | `sku` | `str` | ✅ | Eindeutige Artikelnummer (Stock-Keeping Unit) |
| 7 | `stock_quantity` | `int` | ✅ | Lagerbestand (Anzahl verfügbarer Einheiten, ≥ 0) |
| 8 | `condition` | `str` | ✅ | Zustand des Artikels: `"new"` (neu) oder `"used"` (gebraucht) |
| 9 | `weight` | `float` | – | Gewicht des Produkts in Kilogramm |
| 10 | `image_url` | `str` | – | URL zum Produktbild |
| 11 | `created_at` | `datetime` | – | Zeitstempel der Erstellung (UTC, wird automatisch gesetzt) |
| 12 | `updated_at` | `datetime` | – | Zeitstempel der letzten Änderung (UTC, wird automatisch gesetzt) |

### Validierungsregeln

- **`price`** muss eine Zahl ≥ 0 sein.
- **`stock_quantity`** muss eine ganze Zahl ≥ 0 sein.
- **`condition`** darf nur `"new"` oder `"used"` sein.
- Alle 8 Pflichtfelder müssen beim Anlegen eines Produkts angegeben werden.

---

## Projektstruktur

```
ElectroSwap/
├── app/
│   ├── __init__.py              # Flask App-Factory + MongoDB-Initialisierung
│   ├── models/
│   │   └── product.py           # Product-Klasse (Hauptentität, 12 Attribute)
│   ├── blueprints/
│   │   ├── auth/                # Authentifizierung (Login / Registrierung)
│   │   ├── main/                # Startseite
│   │   ├── products/            # Produktliste, -detail, Neu-Anlegen
│   │   ├── cart/                # Warenkorb
│   │   ├── wishlist/            # Wunschliste
│   │   ├── orders/              # Bestellungen
│   │   ├── reviews/             # Bewertungen
│   │   └── admin/               # Admin-Bereich
│   └── templates/               # Jinja2-Templates (Bootstrap 5)
├── seed_data.py                 # 7 Beispielprodukte mit allen 12 Attributen
├── tests/
│   └── test_products.py         # 25 Unit-Tests (mongomock)
├── requirements.txt
└── run.py
```

## Routen (Produkte)

| Methode | URL | Beschreibung |
|---------|-----|--------------|
| `GET` | `/products/` | Produktliste (filterbar nach Kategorie) |
| `GET` | `/products/<id>` | Produktdetail mit allen Attributen |
| `GET` | `/products/add` | Formular zum Anlegen eines neuen Produkts |
| `POST` | `/products/add` | Neues Produkt speichern |
