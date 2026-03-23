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

## Dokumentation 2.3 und 2.4 – Logisches Datenmodell (NoSQL)

Aus dem konzeptionellen Modell wurde ein **logisches NoSQL-Datenmodell mit 6 Collections** abgeleitet:
`users`, `products`, `orders`, `reviews`, `baskets`, `wishlists`.

Die Umsetzung erfolgt **nicht als ERD**, sondern als strukturierte Beschreibung je Entitätstyp mit:
- Abbildung der Entitätsmengen und Beziehungen
- Pflicht-/Optional-/Variabel-Attributen
- Datentypen
- Je einem Beispiel-MongoDB-Dokument pro Entitätstyp

### 1) Abbildung der Entitätsmengen und Beziehungen

- **Users (1:N) Orders**  
  In `orders.user_id` wird auf `users._id` referenziert.
- **Users (1:N) Reviews**  
  In `reviews.user_id` wird auf `users._id` referenziert.
- **Users (1:1) Basket**  
  `baskets` enthält pro User ein Dokument über `user_id`.
- **Users (1:1) Wishlist**  
  `wishlists` enthält pro User ein Dokument über `user_id`.
- **Products (N:M) Orders**  
  In NoSQL durch **Embedding** in `orders.order_items[]` gelöst (Snapshot beim Kauf).
- **Products (1:N) Reviews**  
  In `reviews.product_id` wird auf `products._id` referenziert.
- **Products (N:M) Basket/Wishlist**  
  In `baskets.items[].product_id` und `wishlists.items[].product_id` referenziert.

### 2) Entitätstypen, Attribute, Pflicht/Optional/Variabel, Datentypen

#### Users (`users`)

| Attribut | Typ | Pflicht |
|---|---|---|
| `_id` | `ObjectId` | Ja |
| `username` | `string` | Ja |
| `email` | `string` | Ja |
| `password_hash` | `string` | Ja |
| `role` | `string` (`admin`/`customer`) | Ja |
| `address.street` | `string` | Ja (kann leer sein) |
| `address.city` | `string` | Ja (kann leer sein) |
| `address.zip_code` | `string` | Ja (kann leer sein) |
| `address.country` | `string` | Ja (kann leer sein) |
| `created_at` | `datetime` | Ja |

**Beispiel-Dokument**
```json
{
  "_id": { "$oid": "65f100000000000000000001" },
  "username": "demo_customer",
  "email": "customer@electroswap.ch",
  "password_hash": "$2b$12$exampleHash",
  "role": "customer",
  "address": {
    "street": "Hauptstr. 10",
    "city": "Bern",
    "zip_code": "3011",
    "country": "Switzerland"
  },
  "created_at": { "$date": "2026-03-23T20:00:00Z" }
}
```

#### Products (`products`)

| Attribut | Typ | Pflicht |
|---|---|---|
| `_id` | `ObjectId` | Ja |
| `name` | `string` | Ja |
| `brand` | `string` | Ja |
| `price` | `number` | Ja |
| `category` | `string` | Ja |
| `stock_quantity` | `number` | Ja |
| `images` | `array<string>` | Ja |
| `description` | `string` | Ja |
| `specs` | `object` | Ja (inhaltlich variabel) |
| `created_at` | `datetime` | Ja |

`specs` ist **variabel** je Kategorie (z. B. CPU, GPU, Monitor).

**Beispiel-Dokument**
```json
{
  "_id": { "$oid": "65f100000000000000000101" },
  "name": "AMD Ryzen 9 7950X",
  "brand": "AMD",
  "price": 549.0,
  "category": "CPU",
  "stock_quantity": 25,
  "images": ["/static/images/products/ryzen-9-7950x.jpg"],
  "description": "16-core, 32-thread unlocked desktop processor with Zen 4 architecture.",
  "specs": {
    "cores": 16,
    "threads": 32,
    "socket": "AM5",
    "base_clock": "4.5 GHz",
    "boost_clock": "5.7 GHz",
    "tdp": 170,
    "cache": "80 MB"
  },
  "created_at": { "$date": "2026-03-23T20:00:00Z" }
}
```

#### Orders (`orders`)

| Attribut | Typ | Pflicht |
|---|---|---|
| `_id` | `ObjectId` | Ja |
| `user_id` | `ObjectId` | Ja |
| `order_date` | `datetime` | Ja |
| `total_price` | `number` | Ja |
| `status` | `string` | Ja |
| `shipping_address.street` | `string` | Ja |
| `shipping_address.city` | `string` | Ja |
| `shipping_address.zip_code` | `string` | Ja |
| `shipping_address.country` | `string` | Ja |
| `order_items` | `array<object>` | Ja |
| `order_items[].product_id` | `ObjectId` | Ja |
| `order_items[].name_at_purchase` | `string` | Ja |
| `order_items[].price_at_purchase` | `number` | Ja |
| `order_items[].quantity` | `number` | Ja |

`order_items` ist eingebettet (Embedding) für unveränderliche Bestellhistorie.

**Beispiel-Dokument**
```json
{
  "_id": { "$oid": "65f100000000000000000201" },
  "user_id": { "$oid": "65f100000000000000000001" },
  "order_date": { "$date": "2026-03-23T20:10:00Z" },
  "total_price": 1098.0,
  "status": "confirmed",
  "shipping_address": {
    "street": "Hauptstr. 10",
    "city": "Bern",
    "zip_code": "3011",
    "country": "Switzerland"
  },
  "order_items": [
    {
      "product_id": { "$oid": "65f100000000000000000101" },
      "name_at_purchase": "AMD Ryzen 9 7950X",
      "price_at_purchase": 549.0,
      "quantity": 2
    }
  ]
}
```

#### Reviews (`reviews`)

| Attribut | Typ | Pflicht |
|---|---|---|
| `_id` | `ObjectId` | Ja |
| `product_id` | `ObjectId` | Ja |
| `user_id` | `ObjectId` | Ja |
| `rating` | `number` (1-5) | Ja |
| `comment` | `string` | Ja (kann leer sein) |
| `verified_purchase` | `boolean` | Ja |
| `created_at` | `datetime` | Ja |

**Beispiel-Dokument**
```json
{
  "_id": { "$oid": "65f100000000000000000301" },
  "product_id": { "$oid": "65f100000000000000000101" },
  "user_id": { "$oid": "65f100000000000000000001" },
  "rating": 5,
  "comment": "Sehr schnell und stabil.",
  "verified_purchase": true,
  "created_at": { "$date": "2026-03-23T20:20:00Z" }
}
```

#### Basket (`baskets`)

| Attribut | Typ | Pflicht |
|---|---|---|
| `_id` | `ObjectId` | Ja |
| `user_id` | `ObjectId` | Ja |
| `items` | `array<object>` | Ja |
| `items[].product_id` | `ObjectId` | Ja |
| `items[].quantity` | `number` | Ja |
| `last_updated` | `datetime` | Ja |

**Beispiel-Dokument**
```json
{
  "_id": { "$oid": "65f100000000000000000401" },
  "user_id": { "$oid": "65f100000000000000000001" },
  "items": [
    {
      "product_id": { "$oid": "65f100000000000000000101" },
      "quantity": 1
    }
  ],
  "last_updated": { "$date": "2026-03-23T20:25:00Z" }
}
```

#### Wishlist (`wishlists`)

| Attribut | Typ | Pflicht |
|---|---|---|
| `_id` | `ObjectId` | Ja |
| `user_id` | `ObjectId` | Ja |
| `name` | `string` | Ja |
| `items` | `array<object>` | Ja |
| `items[].product_id` | `ObjectId` | Ja |
| `items[].added_at` | `datetime` | Ja |

**Beispiel-Dokument**
```json
{
  "_id": { "$oid": "65f100000000000000000501" },
  "user_id": { "$oid": "65f100000000000000000001" },
  "name": "My Wishlist",
  "items": [
    {
      "product_id": { "$oid": "65f100000000000000000101" },
      "added_at": { "$date": "2026-03-23T20:27:00Z" }
    }
  ]
}
```

### 3) Screenshot-Hinweise für die Abgabe

Screenshot: **Konzeptionelles Modell (Übersichtsdiagramm)**  
**Grund:** Zeigt den Ausgangspunkt und alle Entitätstypen/Beziehungen auf einen Blick.  
**Auf dem Screenshot sichtbar:** Users, Products, Orders, Reviews, Basket, Wishlist inkl. Beziehungslinien.

Screenshot: **Logisches Datenmodell (Dokument 2.3/2.4 in README)**  
**Grund:** Nachweis, wie das konzeptionelle Modell konkret in MongoDB umgesetzt wird.  
**Auf dem Screenshot sichtbar:** Mapping-Abschnitt (Embedding/Referencing), Attributtabellen (Pflicht/Optional/Variabel + Datentypen) und die 6 Beispieldokumente.

Screenshot: **MongoDB-Beispiel einer Bestellung (`orders`)**  
**Grund:** Belegt die praktische Umsetzung der N:M-Beziehung Product↔Orders per Embedding und die Snapshot-Strategie.  
**Auf dem Screenshot sichtbar:** `order_items` mit `product_id`, `name_at_purchase`, `price_at_purchase`, `quantity` sowie `shipping_address`.

Vorhandenes Diagramm (Kontext):
![Konzeptionelles Diagramm](https://github.com/user-attachments/assets/5ed4a5a6-6f00-480e-9091-c3dec8415931)
