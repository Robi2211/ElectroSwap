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

## 4.4 GUI, Ergonomie, Design (Dokumentationstext)

Für **GUI und Ergonomie** haben wir auf eine klare, moderne Shop-Oberfläche gesetzt:

- **Konsistente Navigation**: Oben fixe Navigation mit klaren Einstiegen (Shop, Wishlist, Cart, Login/Profil/Admin).
- **Klare visuelle Hierarchie**: Hero-Bereich, Produktkarten, Preis/CTA und Formulare mit eindeutigen Prioritäten.
- **Lesbarkeit im Dark Mode**: Hoher Kontrast zwischen Hintergrund, Karten und Text für längere Nutzung.
- **Direktes Feedback**: Flash-Messages, Hover-States und gut sichtbare Buttons für sichere Interaktion.
- **Responsives Layout**: Mobile-first mit Tailwind (z. B. adaptive Grids, saubere Abstände, skalierende Typografie).

### Verwendetes Farbschema

Das Design basiert auf einem dunklen Premium-Look mit Akzentfarben für Interaktion und Branding:

| Rolle | Farbwert |
|---|---|
| Primärer Akzent (Gelb) | `#facc15` |
| Sekundärer Akzent (Blau) | `#3b82f6` |
| Hintergrund dunkel | `#0f0f1a` |
| Karten-Hintergrund | `#1a1a2e` |
| Flächen/Layer | `#16162a` |
| Border/Trennlinien | `#2a2a4a` |

### Welche Screenshots am besten einfügen?

Für die Doku/Präsentation sind diese Screenshots am aussagekräftigsten:

1. **Startseite mit Hero**  
   Zeigt Branding, Typografie, Farbverlauf und ersten visuellen Eindruck.
2. **Produktübersicht mit Filtern/Suche**  
   Zeigt Ergonomie im Alltag: schnelle Orientierung, Sortierung, Sidebar-Filter.
3. **Produktdetailseite**  
   Zeigt Informationsstruktur (Bilder, Specs, Preis, CTA, Reviews).
4. **Warenkorb + Checkout-Schritt**  
   Zeigt klare User Journey und reduzierte Komplexität beim Kaufprozess.
5. **Login/Registrierung**  
   Zeigt Formular-Ergonomie (Labels, Fokus, klare Eingaben).
6. **Admin-Dashboard (optional)**  
   Zeigt, dass das Design auch im Backoffice konsistent bleibt.

Tipp: Wenn nur 2–3 Screenshots möglich sind, nimm **Startseite**, **Produktübersicht** und **Produktdetailseite**.
