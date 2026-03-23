# ⚡ ElectroSwap – Premium Hardware Shop

> Your one-stop hardware shop — CPUs, GPUs, Monitors and more.

A full-stack e-commerce web application built with **Flask**, **MongoDB**, **Tailwind CSS** and **Alpine.js**. Designed with a premium dark theme inspired by Galaxus.ch/Digitec.ch.

## Tech Stack

| Layer      | Technology                           |
|------------|--------------------------------------|
| Backend    | Python 3.11+ / Flask (Blueprints)    |
| Templating | Jinja2                               |
| Frontend   | Tailwind CSS v3 + Alpine.js          |
| Database   | MongoDB (PyMongo)                    |
| Auth       | bcrypt + Flask-Login                 |
| Forms      | Flask-WTF (CSRF protection)          |

## Features

- **User Authentication** – Register, login, logout, profile with address editing
- **Product Catalog** – Sidebar filters (category, brand, price range), full-text search, sorting
- **Product Detail** – Image gallery, dynamic specs table (different per category), reviews
- **Shopping Cart** – Add, update quantity, remove, persistent per user
- **Wishlist** – Add/remove, move to cart
- **Checkout** – MongoDB transaction (verify stock → reduce → create order → clear cart)
- **Order History** – With snapshot data (price at time of purchase)
- **Reviews** – Only verified purchasers can review (verified_purchase check)
- **Admin Panel** – Product CRUD, stock management, order status updates, dashboard
- **Role-based Access Control** – Customer vs Admin roles

## MongoDB Collections

| Collection | Purpose | Strategy |
|-----------|---------|----------|
| `users` | User accounts with embedded address | Embedding |
| `products` | Catalog with flexible `specs` object | Heterogeneous docs (LB2 4.3) |
| `baskets` | Shopping carts with product references | Referencing |
| `wishlists` | Saved items with product references | Referencing |
| `orders` | Order history with snapshot data | Snapshot principle (LB2 5.2) |
| `reviews` | Product reviews (verified purchase) | Referencing |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start MongoDB (must be running on localhost:27017)
mongod

# 3. Seed the database
python seed_data.py

# 4. Run the application
python run.py
```

Open http://localhost:5000 in your browser.

### Demo Accounts

| Role     | Email                    | Password     |
|----------|--------------------------|--------------|
| Admin    | admin@electroswap.ch     | admin123     |
| Customer | customer@electroswap.ch  | customer123  |

## Project Structure

```
ElectroSwap/
├── app/
│   ├── __init__.py          # App factory, MongoDB setup, indexes
│   ├── models.py            # User model (Flask-Login)
│   ├── auth/routes.py       # Register, login, logout, profile
│   ├── main/routes.py       # Homepage
│   ├── products/routes.py   # Catalog, detail, search
│   ├── cart/routes.py       # Shopping cart CRUD
│   ├── wishlist/routes.py   # Wishlist management
│   ├── orders/routes.py     # Checkout (transaction), order history
│   ├── reviews/routes.py    # Verified reviews
│   ├── admin/routes.py      # Admin dashboard, product/order management
│   └── templates/           # Jinja2 templates with Tailwind CSS
├── seed_data.py             # Database seeder with sample products
├── run.py                   # Entry point
└── requirements.txt
```

## LB2 Criteria Coverage

| Criterion | Description | Implementation |
|-----------|-------------|----------------|
| 2.3, 2.4 | Schema design | 6 collections with proper structure |
| 2.7 | Indexes | Text, category, brand, price, unique email |
| 4.3 | Dynamic data | Heterogeneous `specs` object per product category |
| 5.1 | Indexes | `_ensure_indexes()` in app factory |
| 5.2 | Transactions | Checkout with `start_transaction()` + snapshot orders |
| 5.5 | CRUD | Full CRUD on all collections |
| 5.7 | Extra feature | Wishlist with move-to-cart

## Dokumentationstext für Abgabe (4.4 und 4.5)

### 4.4 GUI, Design, Ergonomie

Die Benutzeroberfläche von **ElectroSwap** wurde mit Fokus auf ein modernes, professionelles und gut lesbares Design umgesetzt.  
Ein konsistentes Farbschema (Dark Theme), klare Abstände, einheitliche UI-Komponenten (Buttons, Karten, Formulare) und eine verständliche Navigation erleichtern die Orientierung.  
Wichtige Aktionen wie Produktsuche, Filterung, Warenkorb und Checkout sind logisch angeordnet und mit wenigen Klicks erreichbar.

Die ergonomische Qualität zeigt sich in:
- klarer Seitenstruktur und visueller Hierarchie,
- eindeutigen Beschriftungen und Call-to-Actions,
- responsiver Darstellung für verschiedene Bildschirmgrössen,
- selbsterklärenden Formularen und Rückmeldungen (z. B. Warenkorb/Bestellung).

Damit ist die Anwendung benutzerfreundlich und ohne lange Einarbeitung nutzbar.

### Welche Screenshots soll ich einfügen?

**Ja, Screenshots solltest du unbedingt einfügen** (zusätzlich zu Screencast oder Live-Demo).  
Für die Bewertung von GUI/Design/Ergonomie sind folgende Screenshots ideal:

1. **Startseite (Home)**
   - Zeigt: Hero-Bereich, Navigation, visuelles Design, klare Einstiegsaktionen.
2. **Produktkatalog mit Filtern**
   - Zeigt: Suchfeld, Kategorie-/Preisfilter, Produktkarten, schnelle Orientierung.
3. **Produktdetailseite**
   - Zeigt: Produktinfos, technische Specs, Preis, Bewertungsbereich, klare Kaufaktion.
4. **Warenkorb + Checkout**
   - Zeigt: Benutzerführung von Auswahl bis Bestellung, Transparenz bei Menge/Preis.
5. **Admin-Dashboard**
   - Zeigt: übersichtliche KPI-Karten, Verwaltungsfunktionen, klare Trennung von Rollen.
6. **Responsive Ansicht (Mobile)**
   - Zeigt: ergonomische Nutzung auf kleinerem Bildschirm (Navigation, Lesbarkeit, Bedienbarkeit).

Tipp für die Doku: Zu jedem Screenshot **1–2 Sätze** schreiben („Was sieht man?“ + „Warum ist das ergonomisch?“).

### 4.5 Technologie, Aufbau der Applikation, Quellcode-Zugriff

#### Verwendete Technologien und Begründung

- **Python 3.11 + Flask (Backend):** leichtgewichtiges, gut strukturierbares Framework; Blueprints erlauben modulare Aufteilung (Auth, Products, Cart, Orders, Admin).
- **MongoDB + PyMongo (Datenhaltung):** geeignet für heterogene Produktdaten mit variablen Attributen im Feld `specs`.
- **Jinja2 (Templating):** serverseitiges Rendering dynamischer Inhalte (Katalog, Details, Historie) bei hoher Wartbarkeit.
- **Tailwind CSS + Alpine.js (Frontend):** modernes, konsistentes UI und leichte Interaktivität ohne schweres Frontend-Framework.
- **Flask-Login, bcrypt, Flask-WTF (Security):** Session-Handling, sicheres Passwort-Hashing, CSRF-Schutz.

#### Aufbau der Applikation (Architektur)

Die Anwendung folgt einem **MVC-ähnlichen Aufbau** mit Application-Factory-Pattern:

- **Model (Datenebene):** MongoDB Collections (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`).
- **Controller (Logik):** Flask-Blueprints in `app/*/routes.py` verarbeiten Requests und steuern Datenbankzugriffe.
- **View (Darstellung):** Jinja2-Templates in `app/templates/**`.
- **Application Factory:** `create_app()` in `app/__init__.py` initialisiert Konfiguration, Extensions und Blueprints.

Wichtige Struktur:
- `run.py` – Startpunkt der Applikation
- `seed_data.py` – Seed-Skript für Demo-Daten
- `app/admin/routes.py` – Admin-Funktionen (Dashboard, Produkt-/Bestellverwaltung)
- `app/orders/routes.py` – Checkout und Bestellhistorie
- `app/templates/` – UI-Templates

#### Quellcode und Berechtigung (Git)

Der Quellcode wird mit **Git/GitHub** verwaltet:
- Repository: `Robi2211/ElectroSwap`
- Versionskontrolle mit Commit-Historie für Nachvollziehbarkeit
- Zusammenarbeit über Branches und Pull Requests

Für die Abgabe soll die Lehrperson Zugriff auf das Repository erhalten (mindestens **Read-Berechtigung**).  
In der Dokumentation kannst du ergänzen:
- Repository-Link
- wer Zugriff erhalten hat (Lehrperson/Team),
- kurzer Hinweis, wie die Applikation gestartet wird (`pip install -r requirements.txt`, `python seed_data.py`, `python run.py`).
