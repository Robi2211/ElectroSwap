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

## Dokumentation für 5.5 und 5.6 (Nachweis)

### 5.5 Voll ausgebaute Applikation

**Alle Entitätsmengen vorhanden (MongoDB Collections):**
- `users` (Benutzerkonten + Adressen)
- `products` (Katalog mit dynamischen Specs)
- `baskets` (Warenkorb)
- `wishlists` (Merkliste)
- `orders` (Bestellhistorie mit Snapshot)
- `reviews` (Produktbewertungen)

**Indexe umgesetzt (Performance + Integrität):**
- `users.email` (unique)
- `products.category`, `products.brand`, `products.price`
- Textindex auf `products.name`, `products.description`, `products.brand`
- `baskets.user_id` (unique), `wishlists.user_id`, `orders.user_id`
- `reviews.product_id` sowie Composite-Unique auf (`product_id`, `user_id`)

**Einfügen / Ändern umgesetzt (Beispiele):**
- Benutzer registrieren + Profiladresse ändern
- Admin: Produkte erstellen, bearbeiten, löschen (vollständiges Produkt-CRUD)
- Warenkorb: Position hinzufügen, Menge ändern, entfernen
- Wishlist: hinzufügen, entfernen, in Warenkorb verschieben
- Bestellungen: Checkout erzeugt neue Order, Admin aktualisiert Bestellstatus
- Reviews: verifizierte Käufer können Bewertungen erfassen

**Mehrere Seiten / Bereiche vorhanden:**
- Startseite, Produktkatalog, Produktdetail
- Login, Registrierung, Profil
- Warenkorb, Wishlist, Bestellverlauf, Checkout
- Admin-Dashboard, Produktverwaltung, Bestellverwaltung

### 5.6 Professionelles Design und intuitive Bedienung (Voraussetzung 5.5)

**Design-Umsetzung:**
- Einheitliches, professionelles User Interface mit Tailwind CSS + klarer Farbpalette (Dark Theme)
- Konsistentes Layout über alle Seiten (gemeinsame Basis-Template-Struktur)
- Visuelle Hierarchie mit Karten, Abständen, Icons und Statusfarben (Success/Error/Info)

**Intuitive Bedienung:**
- Klare Navigation (Top-Navigation + mobile Menüführung)
- Rollenlogik (User/Admin) zeigt nur relevante Menüpunkte
- Direkte Benutzerführung mit Flash-Meldungen nach Aktionen (z. B. „Product updated“, „Order placed“)
- Typische Shop-Workflows ohne Umwege: suchen/filtern → ansehen → Warenkorb/Wishlist → Checkout → Bestellverlauf
