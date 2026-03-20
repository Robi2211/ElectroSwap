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
| 5.7 | Extra feature | Wishlist with move-to-cart |

## Live-Demo / Screencast Ablauf (Kurz-Skript)

### Start (Setup in 20–30 Sekunden)

```bash
# MongoDB muss laufen (Compass optional zeigen)
python seed_data.py
python run.py --port 5001
```

Dann im Browser öffnen: `http://127.0.0.1:5001/`

**Demo-Accounts**
- Admin: `admin@electroswap.ch` / `admin123`
- Customer: `customer@electroswap.ch` / `customer123`

### 4.1 Daten anzeigen (Screencast / Live-Demo)

**Was zeigen**
- Produktliste / Katalog (Daten aus MongoDB)
- Produktdetailseite mit Specs + Reviews
- Orders History (Bestellungen)
- Wishlist
- Warenkorb

**Wo im Code**
- Produkte: `app/products/routes.py`
  - Templates: `app/templates/products/catalog.html`, `app/templates/products/detail.html`
- Warenkorb: `app/cart/routes.py`
  - Template: `app/templates/cart/cart.html`
- Wishlist: `app/wishlist/routes.py`
  - Template: `app/templates/wishlist/wishlist.html`
- Bestellungen: `app/orders/routes.py`
  - Templates: `app/templates/orders/history.html`, `app/templates/orders/order_detail.html`

**Sprechsatz (1–2 Sätze)**
> Alle Views lesen direkt aus MongoDB Collections (`products`, `reviews`, `orders`, etc.) und rendern dynamisch mit Jinja-Templates.

### 4.2 Daten einfügen, ändern, löschen (CRUD) (Screencast / Live-Demo)

**Was zeigen**
- Admin-Panel öffnen: `/admin`
- Create: Produkt hinzufügen
- Update: Produkt bearbeiten (z. B. Preis / Stock)
- Delete: Produkt löschen
- Als User zusätzlich:
  - Cart: add / update quantity / remove
  - Wishlist: add / remove / move-to-cart
  - Checkout: erstellt Order + leert Basket

**Wo im Code**
- Admin CRUD: `app/admin/routes.py`
  - Templates: `app/templates/admin/*`
- Cart CRUD: `app/cart/routes.py`
- Wishlist CRUD: `app/wishlist/routes.py`
- Checkout / Order-Erstellung: `app/orders/routes.py`

**Sprechsatz**
> CRUD ist umgesetzt: Admin verwaltet Produkte (Insert/Update/Delete), User verwaltet Cart/Wishlist; Checkout erstellt Orders und passt den Bestand an.

### 4.3 Datenhandling dynamisch (unterschiedliche Attribute) (Screencast / Live-Demo)

**Was zeigen**
- 2–3 Produkte aus verschiedenen Kategorien öffnen (z. B. CPU / GPU / Monitor)
- Zeigen, dass `specs` unterschiedliche Keys hat (z. B. CPU: `cores`/`threads`, GPU: `cuda_cores`, Monitor: `refresh_rate`)

**Wo im Code**
- Seeder/DB: `seed_data.py` (`specs` ist je Produkt heterogen)
- Darstellung: `app/templates/products/detail.html` (dynamische Specs-Tabelle)

**Sprechsatz**
> MongoDB erlaubt heterogene Dokumente: `products.specs` ist je Kategorie unterschiedlich. Die UI rendert diese Attribute dynamisch.

### 4.4 GUI, Design, Ergonomie (Doku + Screencast / Live-Demo)

**Was zeigen**
- Dark-Theme, responsives Layout
- Navigation: Products / Cart / Wishlist / Orders
- Feedback über Flash-Messages (Success/Error)
- Formularvalidierung (z. B. Checkout-Adresse ist Pflicht)

**Wo im Code**
- Layout: `app/templates/base.html`
- Styling: Tailwind-Klassen in `app/templates/**`
- UX-Feedback: Flash-Messages in mehreren Routes + Anzeige in `base.html`

**Sprechsatz**
> Fokus liegt auf klarer Navigation, konsistenter UI, responsive Layout und sofortigem Feedback bei Aktionen.

### 4.5 Technologie, Aufbau Applikation, Zugriff Quellcode, Screenshots (Doku)

**In die Doku aufnehmen**
- Tech-Stack: Flask, MongoDB, PyMongo, Tailwind, Flask-Login, CSRF
- Projektstruktur + Blueprints
- DB-Collections + kurzer Zweck
- Wichtige Dateien:
  - App-Factory + DB Setup: `app/__init__.py`
  - User-Model: `app/models.py`
  - Entry Point: `run.py`
  - Seeder: `seed_data.py`
  - Basis-Doku: `README.md`

**Screenshots (empfohlen)**
- Startseite/Katalog
- Produktdetail (mit Specs)
- Cart/Wishlist
- Checkout/Orders
- Admin-Panel
- MongoDB Compass (Collections/Beispieldokument)

### Wichtige LB2-Punkte (Kurzargumente)

**A) Indexes (Performance / Kriterium 5.1)**
- Ort: `app/__init__.py` (`_ensure_indexes()`)
- Sprechsatz:
  > Ich erstelle DB-Indexes (email unique, text search, category/brand/price), damit Suche & Filter performant sind.

**B) Transaktionen / Bestellprozess (Kriterium 5.2)**
- Ort: `app/orders/routes.py` (Checkout mit Transaction + Standalone-Fallback)
- Sprechsatz:
  > Checkout reduziert Stock, erstellt Order (Snapshot) und leert Basket – idealerweise atomar via Transaktion; lokal gibt es einen Fallback für Standalone-MongoDB.

**C) Genügend Testdaten**
- Ort: `seed_data.py`
- Sprechsatz:
  > Der Seeder generiert konsistente, realistische Testdaten für eine stabile Live-Demo mit mehreren Usern, Produkten, Reviews und Bestellungen.
