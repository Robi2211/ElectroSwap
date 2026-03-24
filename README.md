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

## BIM 2.3 – Attribute (Pflicht / Optional / Bedingung / Datentyp)

### `users`

| Attribut | Pflicht? | Datentyp | Bedingung / Regel |
|---|---|---|---|
| `_id` | Ja | `ObjectId` | Automatisch von MongoDB |
| `username` | Ja | `string` | Mindestens 3 Zeichen, eindeutig |
| `email` | Ja | `string` | Eindeutig, wird lowercase gespeichert; aktuelle App-Validierung prüft mindestens auf `@` |
| `password_hash` | Ja | `string` | bcrypt-Hash (kein Klartext-Passwort) |
| `role` | Ja | `string` | `"customer"` oder `"admin"` |
| `address` | Ja | `object` | Enthält Felder unten |
| `address.street` | Ja (im Objekt) | `string` | Darf leer sein; bei Checkout muss Adresse vollständig sein |
| `address.city` | Ja (im Objekt) | `string` | Darf leer sein; bei Checkout muss Adresse vollständig sein |
| `address.zip_code` | Ja (im Objekt) | `string` | Darf leer sein; bei Checkout muss Adresse vollständig sein |
| `address.country` | Ja (im Objekt) | `string` | Darf leer sein; bei Checkout muss Adresse vollständig sein |
| `created_at` | Ja | `datetime` | UTC-Zeitstempel |

### `products`

| Attribut | Pflicht? | Datentyp | Bedingung / Regel |
|---|---|---|---|
| `_id` | Ja | `ObjectId` | Automatisch von MongoDB |
| `name` | Ja | `string` | Produktname |
| `brand` | Ja | `string` | Hersteller/Marke |
| `price` | Ja | `float` | Aktuell als `float` in CHF implementiert (auf 2 Dezimalen gerundet) |
| `category` | Ja | `string` | Erlaubte Kategorien: CPU, GPU, Monitor, Motherboard, PSU, RAM, Case, Storage, Cooling, Peripherals |
| `stock_quantity` | Ja | `int` | Lagerbestand |
| `images` | Ja | `array[string]` | Wenn leer, wird Placeholder-Bild gesetzt |
| `description` | Ja | `string` | Beschreibung (kann leer sein) |
| `specs` | Ja | `object` | Flexible, kategorieabhängige Attribute (heterogene Dokumente) |
| `created_at` | Ja | `datetime` | UTC-Zeitstempel |

### `baskets`

| Attribut | Pflicht? | Datentyp | Bedingung / Regel |
|---|---|---|---|
| `_id` | Ja | `ObjectId` | Automatisch von MongoDB |
| `user_id` | Ja | `ObjectId` | Referenz auf `users._id` |
| `items` | Ja | `array[object]` | Mindestens ein Eintrag beim Erstellen |
| `items[].product_id` | Ja | `ObjectId` | Referenz auf `products._id` |
| `items[].quantity` | Ja | `int` | Muss >= 1 sein |
| `last_updated` | Ja | `datetime` | UTC-Zeitstempel |

### `wishlists`

| Attribut | Pflicht? | Datentyp | Bedingung / Regel |
|---|---|---|---|
| `_id` | Ja | `ObjectId` | Automatisch von MongoDB |
| `user_id` | Ja | `ObjectId` | Referenz auf `users._id` |
| `name` | Optional | `string` | Standardwert beim Erstellen: `"My Wishlist"` |
| `items` | Ja | `array[object]` | Liste gespeicherter Produkte |
| `items[].product_id` | Ja | `ObjectId` | Referenz auf `products._id` |
| `items[].added_at` | Optional | `datetime` | UTC-Zeitstempel (wird beim Hinzufügen gesetzt) |

### `orders`

| Attribut | Pflicht? | Datentyp | Bedingung / Regel |
|---|---|---|---|
| `_id` | Ja | `ObjectId` | Automatisch von MongoDB |
| `user_id` | Ja | `ObjectId` | Referenz auf `users._id` |
| `order_date` | Ja | `datetime` | UTC-Zeitstempel |
| `total_price` | Ja | `float` | Aktuell als `float` in CHF implementiert; Gesamtsumme der Bestellung |
| `status` | Ja | `string` | Initial `"confirmed"`, Admin kann Status ändern |
| `shipping_address` | Ja | `object` | Muss beim Checkout vollständig ausgefüllt sein |
| `shipping_address.street` | Ja | `string` | Nicht leer bei Checkout |
| `shipping_address.city` | Ja | `string` | Nicht leer bei Checkout |
| `shipping_address.zip_code` | Ja | `string` | Nicht leer bei Checkout |
| `shipping_address.country` | Ja | `string` | Nicht leer bei Checkout |
| `order_items` | Ja | `array[object]` | Snapshot-Prinzip (Werte zum Kaufzeitpunkt) |
| `order_items[].product_id` | Ja | `ObjectId` | Referenz auf `products._id` |
| `order_items[].name_at_purchase` | Ja | `string` | Name zum Kaufzeitpunkt |
| `order_items[].price_at_purchase` | Ja | `float` | Aktuell als `float`; Snapshot-Preis zum Kaufzeitpunkt |
| `order_items[].quantity` | Ja | `int` | Anzahl pro Position |

### `reviews`

| Attribut | Pflicht? | Datentyp | Bedingung / Regel |
|---|---|---|---|
| `_id` | Ja | `ObjectId` | Automatisch von MongoDB |
| `product_id` | Ja | `ObjectId` | Referenz auf `products._id` |
| `user_id` | Ja | `ObjectId` | Referenz auf `users._id` |
| `rating` | Ja | `int` | Wertebereich 1–5 |
| `comment` | Optional | `string` | Freitext |
| `verified_purchase` | Optional | `bool` | In App-Flow immer `true`; Review nur nach Kauf erlaubt |
| `created_at` | Ja | `datetime` | UTC-Zeitstempel |

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
