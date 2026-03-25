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

ElectroSwap ist als Fullstack-Webapplikation mit **serverseitigem Rendering** umgesetzt. Im Gegensatz zu einer getrennten SPA-/API-Architektur liegt die Anwendung als Flask-Projekt in einem gemeinsamen Codebestand vor: Request-Handling (Blueprints), Business-Logik, Datenzugriff und HTML-Rendering arbeiten eng zusammen.

### Frontend

Das Frontend wird über **Jinja2-Templates** (im Verzeichnis `app/templates/` inkl. Unterordnern) gerendert.  
Für das UI kommen **Tailwind CSS** und **Alpine.js** zum Einsatz:

- Tailwind CSS für ein konsistentes, responsives Design
- Alpine.js für leichte Interaktivität (z. B. UI-States)
- Serverseitiges Rendering für Seiten wie Katalog, Produktdetail, Warenkorb, Checkout und Admin

### Backend

Das Backend basiert auf **Python 3.11+ und Flask**. Die Struktur folgt einem MVC-ähnlichen Ansatz:

- **Controller/Logik:** Flask-Blueprints in `app/*/routes.py` (z. B. `auth`, `products`, `cart`, `orders`, `admin`)
- **Model/Datenzugriff:** MongoDB-Collections über **PyMongo**
- **View/Darstellung:** Jinja2-Templates

Zusätzlich wird das **Application-Factory-Pattern** verwendet (`create_app()` in `app/__init__.py`).  
Sicherheitsrelevante Bausteine sind:

- **Flask-Login** (Session-Management, Rollenprüfung)
- **bcrypt** (Passwort-Hashing)
- **Flask-WTF / CSRFProtect** (CSRF-Schutz bei Formularen)

### Datenbankkonfiguration

Die MongoDB-Verbindung wird über `MONGO_URI` konfiguriert und standardmäßig auf eine lokale Instanz gesetzt:

`mongodb://localhost:27017/electroswap`

Der Datenbankname wird aus der URI abgeleitet (`app/__init__.py`). Beim Start werden zudem zentrale Indexe automatisch erstellt (`_ensure_indexes()` in `app/__init__.py`), z. B. für `users.email`, `products`-Suche und `reviews`-Eindeutigkeit pro Nutzer/Produkt.

### Wichtige Routen (Web-Endpunkte)

> Hinweis: ElectroSwap nutzt primär serverseitige Web-Routen (keine separate `/api/...`-JWT-API).

| Bereich | Zugriff | Methode | Route | Beschreibung |
|---|---|---|---|---|
| Main | Public | GET | `/` | Startseite mit Featured Products |
| Auth | Public | GET/POST | `/auth/register` | Benutzer registrieren |
| Auth | Public | GET/POST | `/auth/login` | Benutzer einloggen |
| Auth | Login | GET | `/auth/logout` | Benutzer ausloggen |
| Auth | Login | GET/POST | `/auth/profile` | Profil/Adresse verwalten |
| Products | Public | GET | `/products/` | Katalog mit Suche, Filter, Sortierung |
| Products | Public | GET | `/products/<product_id>` | Produktdetail inkl. Reviews |
| Cart | Login | GET | `/cart/` | Warenkorb anzeigen |
| Cart | Login | POST | `/cart/add/<product_id>` | Produkt zum Warenkorb hinzufügen |
| Cart | Login | POST | `/cart/update/<product_id>` | Menge aktualisieren |
| Cart | Login | POST | `/cart/remove/<product_id>` | Produkt entfernen |
| Wishlist | Login | GET | `/wishlist/` | Wunschliste anzeigen |
| Wishlist | Login | POST | `/wishlist/add/<product_id>` | Zur Wunschliste hinzufügen |
| Wishlist | Login | POST | `/wishlist/remove/<product_id>` | Aus Wunschliste entfernen |
| Wishlist | Login | POST | `/wishlist/move-to-cart/<product_id>` | In Warenkorb verschieben |
| Orders | Login | GET | `/orders/` | Bestellhistorie |
| Orders | Login | GET | `/orders/<order_id>` | Bestelldetail |
| Orders | Login | GET/POST | `/orders/checkout` | Checkout-Prozess |
| Reviews | Login | POST | `/reviews/add/<product_id>` | Bewertung (Verified Purchase) |
| Admin | Admin | GET | `/admin/` | Dashboard |
| Admin | Admin | GET | `/admin/products` | Produktverwaltung |
| Admin | Admin | GET/POST | `/admin/products/create` | Produkt erstellen |
| Admin | Admin | GET/POST | `/admin/products/edit/<product_id>` | Produkt bearbeiten |
| Admin | Admin | POST | `/admin/products/delete/<product_id>` | Produkt löschen |
| Admin | Admin | GET | `/admin/orders` | Bestellungen verwalten |
| Admin | Admin | POST | `/admin/orders/<order_id>/status` | Bestellstatus aktualisieren |

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
