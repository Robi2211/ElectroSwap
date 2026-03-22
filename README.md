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

## Konzeptionelles Datenmodell (Erklärung zum Diagramm)

Das konzeptionelle Modell beschreibt die fachlichen Hauptobjekte des Shops und ihre Beziehungen:

- **User**: Konto eines Kunden oder Admins.
- **Products**: Verkaufbare Hardware-Artikel.
- **Reviews**: Bewertungen, die ein User zu einem Produkt schreibt.
- **Wishlist**: Merkliste eines Users mit gespeicherten Produkten.
- **Orders/Basket**: Warenkorb- und Bestellkontext, in dem Produkte einem User zugeordnet sind.

### Beziehungen und Kardinalitäten

1. **User ↔ Reviews**  
   Ein User kann **0..n Reviews** schreiben, eine Review gehört immer zu **genau 1 User**.

2. **Products ↔ Reviews**  
   Ein Produkt kann **0..n Reviews** haben, eine Review bezieht sich auf **genau 1 Produkt**.

3. **User ↔ Wishlist**  
   Ein User hat fachlich **0..1 aktive Wishlist**, eine Wishlist gehört zu **genau 1 User**.

4. **Wishlist ↔ Products**  
   Eine Wishlist enthält **0..n Produkte**, und ein Produkt kann in **0..n Wishlists** vorkommen  
   (also eine **n:m-Beziehung**, technisch über die `items`-Liste gelöst).

5. **User ↔ Orders/Basket**  
   Ein User kann **0..1 aktiven Basket** und über die Zeit **0..n Orders** haben; diese gehören jeweils zu **genau 1 User**.

6. **Orders/Basket ↔ Products**  
   Basket/Order enthalten **1..n Produkte**, ein Produkt kann in **0..n Baskets/Orders** vorkommen  
   (ebenfalls **n:m**, technisch über `items` bzw. `order_items`).

### Wichtige fachliche Regel

- **Review nur bei Kauf**: Reviews sind an einen verifizierten Kauf gekoppelt (Verified Purchase).

## Einfügebefehle pro Entitätstyp (MongoDB)

Falls alle Entitäten auf einmal eingefügt werden sollen, kann das bestehende Seed-Skript verwendet werden:

```bash
python seed_data.py
```

Für einzelne Entitäten können die folgenden `mongosh`-Befehle verwendet werden (jeweils mit allen Attributen aus dem Code):

```javascript
// users
db.users.insertOne({
  username: "max",
  email: "max@example.com",
  password_hash: "$2b$12$REPLACE_WITH_BCRYPT_HASH",
  role: "customer", // oder "admin"
  address: {
    street: "Musterstrasse 1",
    city: "Zürich",
    zip_code: "8000",
    country: "Switzerland"
  },
  created_at: new Date()
})

// products
db.products.insertOne({
  name: "Beispiel Produkt",
  brand: "Beispiel Marke",
  price: 199.90,
  category: "GPU", // z.B. CPU, GPU, Monitor, Motherboard, PSU, RAM, Case, Storage, Cooling, Peripherals
  stock_quantity: 10,
  images: ["/static/images/products/example.jpg"],
  description: "Kurze Produktbeschreibung",
  specs: {
    memory: "12 GB",
    interface: "PCIe 4.0 x16"
  },
  created_at: new Date()
})

// baskets
db.baskets.insertOne({
  user_id: ObjectId("64b000000000000000000001"),
  items: [
    { product_id: ObjectId("64b000000000000000000101"), quantity: 2 }
  ],
  last_updated: new Date()
})

// wishlists
db.wishlists.insertOne({
  user_id: ObjectId("64b000000000000000000001"),
  name: "My Wishlist",
  items: [
    { product_id: ObjectId("64b000000000000000000101"), added_at: new Date() }
  ]
})

// orders
db.orders.insertOne({
  user_id: ObjectId("64b000000000000000000001"),
  order_date: new Date(),
  total_price: 399.80,
  status: "confirmed",
  shipping_address: {
    street: "Musterstrasse 1",
    city: "Zürich",
    zip_code: "8000",
    country: "Switzerland"
  },
  order_items: [
    {
      product_id: ObjectId("64b000000000000000000101"),
      name_at_purchase: "Beispiel Produkt",
      price_at_purchase: 199.90,
      quantity: 2
    }
  ]
})

// reviews
db.reviews.insertOne({
  product_id: ObjectId("64b000000000000000000101"),
  user_id: ObjectId("64b000000000000000000001"),
  rating: 5,
  comment: "Sehr gutes Produkt",
  verified_purchase: true,
  created_at: new Date()
})
```

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
