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

## 4.6 Features

- **User Authentication** – Registrierung, Login, Logout, Profil inkl. Adressverwaltung
- **Admin Panel** – Produktverwaltung (CRUD), Lagerbestand, Bestellstatus, Dashboard
- **Role-based Access Control** – Unterscheidung zwischen Kunde und Admin

## 4.7 Aufbau der Applikation

### Architekturansatz

Die Anwendung folgt einem praxisnahen MVC-ähnlichen Aufbau:

- **Model (Datenebene):**  
  MongoDB-Dokumente und Datenzugriffe über PyMongo (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`)
- **Controller (Logik):**  
  Flask-Blueprints (`app/*/routes.py`) verarbeiten Requests, validieren Eingaben und steuern Datenbankoperationen
- **View (Darstellung):**  
  Jinja2-Templates (`app/templates/**`) rendern die HTML-Oberfläche

Zusätzlich wird das Application-Factory-Pattern verwendet (`create_app()` in `app/__init__.py`).  
Dadurch bleiben Konfiguration, Initialisierung und Struktur übersichtlich und wartbar.

### Code- und Dateistruktur (Überblick)

- `run.py` – Einstiegspunkt zum Starten der Anwendung
- `app/__init__.py` – Application Factory, Initialisierung von Flask, MongoDB, Login, CSRF und Blueprints
- `app/models.py` – User-Logik für Flask-Login
- `app/auth/routes.py` – Registrierung, Login, Logout, Profilverwaltung
- `app/products/routes.py` – Produktkatalog, Suche, Filter, Detailseiten
- `app/cart/routes.py` – Warenkorb-Funktionen (hinzufügen, ändern, entfernen)
- `app/orders/routes.py` – Checkout-Prozess, Bestellungen, Historie
- `app/reviews/routes.py` – Bewertungen inkl. Verified-Purchase-Prüfung
- `app/admin/routes.py` – Admin-Dashboard und Verwaltungsfunktionen
- `app/templates/` – Frontend (Jinja2 + Tailwind CSS)
- `seed_data.py` – Script zum Befüllen der Datenbank

### Technologie / Aufbau der Applikation

ElectroSwap ist als Fullstack-Webapplikation umgesetzt und basiert auf Flask mit serverseitigem Rendering.  
Die Fachlogik ist modular in Blueprints aufgeteilt (z. B. Authentifizierung, Produkte, Warenkorb, Bestellungen, Admin), was Wartung und Erweiterbarkeit verbessert.

Im Frontend kommen Jinja2, Tailwind CSS und Alpine.js zum Einsatz. Dadurch bleibt das UI modern, responsiv und gleichzeitig leichtgewichtig ohne komplexes SPA-Framework.

Im Backend steuern Flask-Routen die Business-Logik direkt und greifen über PyMongo auf MongoDB zu.  
Die Datenhaltung nutzt flexible Dokumente (insbesondere `products.specs`), sodass unterschiedliche technische Produktattribute je Kategorie sauber gespeichert werden können.

### Datenbankkonfiguration

Der Zugriff auf die Datenbank wird über eine konfigurierbare MongoDB-URI gesteuert.

- Standard: `mongodb://localhost:27017/electroswap`
- Konfiguration über Umgebungsvariable: `MONGO_URI`

Zusätzlich existiert mit `seed_data.py` ein Seed-Mechanismus, mit dem Test- und Demodaten automatisiert erstellt werden können.

### Anfragen / Endpunkte (Überblick)

| Bereich | Zugriff | Methode | Endpoint | Beschreibung |
|--------|---------|---------|----------|--------------|
| Auth | Public | GET/POST | `/auth/register` | Registriert einen neuen Benutzer |
| Auth | Public | GET/POST | `/auth/login` | Login eines Benutzers |
| Auth | Session | GET | `/auth/logout` | Logout |
| Auth | Session | GET/POST | `/auth/profile` | Profil inkl. Adresse anzeigen/bearbeiten |
| Produkte | Public | GET | `/products/` | Produktkatalog mit Suche/Filter |
| Produkte | Public | GET | `/products/{id}` | Produktdetailseite |
| Warenkorb | Session | GET | `/cart/` | Warenkorb anzeigen |
| Warenkorb | Session | POST | `/cart/add/{product_id}` | Produkt in Warenkorb legen |
| Warenkorb | Session | POST | `/cart/update/{product_id}` | Menge im Warenkorb ändern |
| Warenkorb | Session | POST | `/cart/remove/{product_id}` | Produkt aus Warenkorb entfernen |
| Wishlist | Session | GET | `/wishlist/` | Merkliste anzeigen |
| Wishlist | Session | POST | `/wishlist/add/{product_id}` | Produkt zur Merkliste hinzufügen |
| Wishlist | Session | POST | `/wishlist/remove/{product_id}` | Produkt aus Merkliste entfernen |
| Wishlist | Session | POST | `/wishlist/move-to-cart/{product_id}` | Von Merkliste in Warenkorb verschieben |
| Bestellungen | Session | GET/POST | `/orders/checkout` | Checkout durchführen |
| Bestellungen | Session | GET | `/orders/` | Bestellhistorie anzeigen |
| Bestellungen | Session | GET | `/orders/{order_id}` | Bestell-Details anzeigen |
| Reviews | Session | POST | `/reviews/add/{product_id}` | Bewertung erfassen (verifizierter Kauf) |
| Admin | Admin | GET | `/admin/` | Admin-Dashboard |
| Admin | Admin | GET | `/admin/products` | Produktverwaltung |
| Admin | Admin | GET/POST | `/admin/products/create` | Produkt erstellen |
| Admin | Admin | GET/POST | `/admin/products/edit/{product_id}` | Produkt bearbeiten |
| Admin | Admin | POST | `/admin/products/delete/{product_id}` | Produkt löschen |
| Admin | Admin | GET | `/admin/orders` | Bestellungen verwalten |
| Admin | Admin | POST | `/admin/orders/{order_id}/status` | Bestellstatus aktualisieren |
