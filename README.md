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

## Technologie / Aufbau der Applikation (ausformuliert)

ElectroSwap ist als serverseitig gerenderte Fullstack-Webapplikation umgesetzt und folgt einer klaren Trennung von fachlichen Modulen im Backend sowie einer strukturierten Template-Ebene im Frontend. Die Anwendung wird in `app/` über Flask-Blueprints organisiert (z. B. `auth`, `products`, `cart`, `orders`, `reviews`, `admin`). Dadurch können einzelne Funktionsbereiche unabhängig erweitert und gewartet werden.

### Backend

Das Backend basiert auf **Python 3.11+** und **Flask**. Flask wurde gewählt, weil das Framework leichtgewichtig ist und sich sehr gut modular mit Blueprints strukturieren lässt.  
Die Initialisierung erfolgt über das **Application-Factory-Pattern** (`create_app()` in `app/__init__.py`). Damit bleiben Konfiguration, Extension-Setup (Login, CSRF, MongoDB), Index-Erstellung und Registrierung der Blueprints sauber voneinander getrennt.

Sicherheits- und Benutzerverwaltungsfunktionen:

- **Flask-Login** für Session-Management und geschützte Bereiche
- **bcrypt** für sicheres Hashing von Passwörtern
- **Flask-WTF / CSRFProtect** zum Schutz vor CSRF-Angriffen in Formularen

### Frontend

Das Frontend wird serverseitig mit **Jinja2** gerendert. Dieses Rendering-Modell passt zum Projekt, da Produktkatalog, Detailseiten, Warenkorb, Checkout und Admin-Masken direkt aus den Backend-Daten aufgebaut werden können.  
Für das UI werden **Tailwind CSS** und **Alpine.js** verwendet:

- **Tailwind CSS** für konsistente, responsive und schnell anpassbare Oberflächen
- **Alpine.js** für leichte Interaktivität (z. B. UI-Zustände), ohne ein schweres SPA-Framework

### Datenhaltung (MongoDB)

Die Datenhaltung erfolgt über **MongoDB** mit **PyMongo**. MongoDB ist geeignet, weil Produktdaten je nach Kategorie unterschiedliche technische Eigenschaften enthalten und flexibel im Feld `specs` gespeichert werden können.  
Der Datenbankzugriff wird über `MONGO_URI` konfiguriert (Standard in der App: `mongodb://localhost:27017/electroswap`), kann aber per Umgebungsvariable für andere Umgebungen überschrieben werden.

Zusätzlich gibt es mit `seed_data.py` einen Seed-Mechanismus, um Demo-Daten für Entwicklung und Präsentation schnell bereitzustellen.

### Architekturansatz (MVC-ähnlich)

Die Anwendung folgt einem praxisnahen **MVC-ähnlichen Aufbau**:

- **Model (Datenebene):** MongoDB-Collections und Datenzugriffe via PyMongo (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`)
- **Controller (Logik):** Flask-Blueprint-Routen in `app/*/routes.py` validieren Eingaben, steuern Geschäftslogik und Datenbankoperationen
- **View (Darstellung):** Jinja2-Templates in `app/templates/**` rendern die HTML-Oberfläche

### API-Anfragen / Routenübersicht

| Bereich | Zugriff | Methode | Endpoint | Beschreibung |
|---|---|---|---|---|
| Main | Public | GET | `/` | Startseite mit Featured-Produkten |
| Auth | Public | GET/POST | `/auth/register` | Registrierung eines Benutzers |
| Auth | Public | GET/POST | `/auth/login` | Login |
| Auth | Login | GET | `/auth/logout` | Logout |
| Auth | Login | GET/POST | `/auth/profile` | Profil inkl. Adressverwaltung |
| Products | Public | GET | `/products/` | Produktkatalog mit Suche, Filter, Sortierung |
| Products | Public | GET | `/products/<product_id>` | Produktdetailseite |
| Cart | Login | GET | `/cart/` | Warenkorb anzeigen |
| Cart | Login | POST | `/cart/add/<product_id>` | Produkt zum Warenkorb hinzufügen |
| Cart | Login | POST | `/cart/update/<product_id>` | Menge im Warenkorb ändern |
| Cart | Login | POST | `/cart/remove/<product_id>` | Produkt aus Warenkorb entfernen |
| Wishlist | Login | GET | `/wishlist/` | Wunschliste anzeigen |
| Wishlist | Login | POST | `/wishlist/add/<product_id>` | Produkt zur Wunschliste hinzufügen |
| Wishlist | Login | POST | `/wishlist/remove/<product_id>` | Produkt aus Wunschliste entfernen |
| Wishlist | Login | POST | `/wishlist/move-to-cart/<product_id>` | Produkt von Wunschliste in Warenkorb verschieben |
| Orders | Login | GET | `/orders/` | Bestellhistorie |
| Orders | Login | GET | `/orders/<order_id>` | Bestelldetail |
| Orders | Login | GET/POST | `/orders/checkout` | Checkout mit Bestandsprüfung und Bestellung |
| Reviews | Login | POST | `/reviews/add/<product_id>` | Bewertung (nur bei verifiziertem Kauf) |
| Admin | Admin | GET | `/admin/` | Dashboard mit Kennzahlen |
| Admin | Admin | GET | `/admin/products` | Produktverwaltung |
| Admin | Admin | GET/POST | `/admin/products/create` | Produkt erstellen |
| Admin | Admin | GET/POST | `/admin/products/edit/<product_id>` | Produkt bearbeiten |
| Admin | Admin | POST | `/admin/products/delete/<product_id>` | Produkt löschen |
| Admin | Admin | GET | `/admin/orders` | Bestellverwaltung |
| Admin | Admin | POST | `/admin/orders/<order_id>/status` | Bestellstatus ändern |

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
