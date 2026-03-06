# ⚡ Electro Swap – Hardware Online Shop

A professional hardware online shop built with **Flask** and **MongoDB** (PyMongo).

## Features

- **Product Catalog** – 22 realistic hardware items across 9 categories (CPU, GPU, SSD, Monitor, RAM, Motherboard, PSU, Case, Cooler, Peripheral)
- **User Authentication** – Register/Login with Werkzeug password hashing
- **Shopping Basket** – Add, update quantity, remove items
- **Checkout with Transaction Logic** – Stock validation → order creation (snapshot principle) → stock reduction → basket clearing
- **Order History** – User dashboard showing past orders with snapshot data
- **Review System** – Only purchasers can leave reviews (linked to orders)
- **Admin Dashboard** – Analytics with MongoDB Aggregation Pipeline (avg price per category)
- **Search & Filter** – Search bar and category sidebar
- **Dark Mode UI** – Bootstrap 5 dark tech theme with custom CSS

## Project Structure

```
ElectroSwap/
├── app.py              # Flask routes, session handling, auth
├── database.py         # MongoDB logic, seeding, aggregations, indexes
├── requirements.txt    # Python dependencies
├── static/
│   └── style.css       # Custom dark theme styling
└── templates/
    ├── layout.html     # Base template (navbar, footer, flash messages)
    ├── index.html      # Product listing with search and category sidebar
    ├── product_detail.html  # Product details with specs and reviews
    ├── basket.html     # Shopping cart
    ├── login.html      # Login form
    ├── register.html   # Registration form
    ├── orders.html     # Order history
    └── admin.html      # Admin analytics dashboard
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure MongoDB is running on localhost:27017

# Seed the database (via browser)
# Navigate to http://localhost:5000/seed

# Run the application
python app.py
```

## IET-165 LB2 Criteria Coverage

| Criterion | Description | Implementation |
|-----------|-------------|----------------|
| 2.5 | Password hashing | Werkzeug `generate_password_hash` / `check_password_hash` |
| 2.7 | Heterogeneous attributes | `specs` field varies by category (CPU, SSD, Monitor, etc.) |
| 2.8 | Aggregation Pipeline | `get_analytics()` – avg price per category |
| 2.9 | 20+ realistic items | `seed_db()` – 22 hardware products |
| 5.1 | Indexes | `create_indexes()` on `name` and `category` |
| 5.2 | Transaction Logic | `checkout()` – stock check → order → reduce stock → clear basket |