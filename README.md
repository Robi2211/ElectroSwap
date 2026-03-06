# ⚡ ElectroSwap – Hardware Online Shop

A complete hardware online shop built with **Python (Flask)** and **MongoDB (PyMongo)**.

## Features

| Criterion | Description | Implementation |
|-----------|-------------|----------------|
| 2.2–2.3 | Five collections | `database.py` – Users, Products, Baskets, Orders, Reviews |
| 2.4 | ≥ 8 attributes on Products | name, brand, price, category, stock, description, image\_url, specs, created\_at |
| 2.7 | Heterogeneous data | `specs` sub-document varies by category (CPU → cores/socket, Monitor → resolution/refresh\_rate) |
| 2.8 | Aggregation Pipeline | `avg_price_per_category()` in `database.py` |
| 2.9 | 20+ data items | `seed_db()` inserts 24 realistic hardware products |
| 2.6 | CRUD for all collections | Add / Update / Delete functions per collection |
| 5.1 | Indexes | Indexes on `name` and `category` |
| 5.2 | Transaction logic | `checkout()` validates stock → reduces stock → creates order |
| 5.5–5.6 | Web application | Flask routes + Bootstrap 5 templates |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure MongoDB is running on localhost:27017

# 3. Run the application
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Project Structure

```
ElectroSwap/
├── app.py              # Flask application & routes
├── database.py         # MongoDB data access layer (5 collections)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── base.html               # Shared layout (Bootstrap 5)
│   ├── index.html              # Home – product listing with filters
│   ├── product.html            # Product detail – specs & reviews
│   ├── basket.html             # Shopping basket
│   ├── checkout.html           # Checkout form
│   └── order_confirmation.html # Order success page
└── static/
    └── images/                 # Product image placeholders
```