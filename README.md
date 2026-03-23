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

## Konzeptionelles Datenmodell (Dokumentation 2.2)

Das **konzeptionelle Datenmodell** beschreibt die wichtigsten Objekttypen eines Online-Shops und ihre Beziehungen, unabhängig vom konkreten Datenbanksystem (SQL/NoSQL).

### Entitätsmengen (Objekttypen)

- **User** (Kunde oder Admin über Attribut `role`)
- **Product** (verkaufte Produkte)
- **Review** (Produktbewertungen)
- **Wishlist** (Merkliste eines Users)
- **Order** (abgeschlossene Bestellung)
- **Basket** (aktiver Warenkorb)

### Beziehungen (vereinfacht)

- Ein **User** kann mehrere oder keine **Review** schreiben; jede **Review** gehört genau einem **User**.
- Ein **Product** kann mehrere oder keine **Review** haben; jede **Review** gehört genau zu einem **Product**.
- Ein **User** hat maximal eine **Wishlist**; diese gehört genau diesem **User**.
- Eine **Wishlist** kann mehrere oder keine **Products** enthalten, und ein **Product** kann in mehreren oder keiner **Wishlist** vorkommen (n:m).
- Ein **User** kann mehrere oder keine **Order** haben und zusätzlich einen aktiven **Basket**.
- Eine **Order** kann mehrere oder keine **Products** enthalten, und **Products** können in vielen **Orders** vorkommen (n:m).
- Ein **Basket** kann mehrere oder keine **Products** enthalten, und **Products** können in vielen **Baskets** vorkommen (n:m).

### Fachregel

- **Reviews sind nur erlaubt, wenn das Produkt tatsächlich gekauft wurde** (*Verified Purchase*).

### Hinweis zu Attributen

Im konzeptionellen Modell werden Entitätstypen mit ihren Attributen beschrieben (**ohne IDs**). Mindestens eine Entitätsmenge muss **8 oder mehr Attribute** enthalten.

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
