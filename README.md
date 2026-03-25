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

### Präsentationshilfe: Folie „Welche Technologien stecken dahinter?“

**Was auf die Folie kann (kurz & klar):**
- **Frontend:** Jinja2 Templates, Tailwind CSS v3, Alpine.js (interaktive UI ohne schweres Frontend-Framework)
- **Backend:** Python 3.11+ mit Flask und Blueprints (**kein Node.js / Express**)
- **Datenbank:** MongoDB mit PyMongo, Textindex für Suche, Transaktionen im Checkout
- **Sonstige Technologien:** Flask-Login, bcrypt (Passwort-Hashing), Flask-WTF (CSRF-Schutz), Font Awesome

**Was du dazu sagen kannst (Sprechtext):**
> „Wir haben bewusst einen pragmatischen Full-Stack gewählt: Im Backend nutzen wir Python mit Flask und Blueprints, weil diese Architektur für unsere Module wie Auth, Produkte, Warenkorb und Bestellungen sehr klar und wartbar ist.  
> Im Frontend kombinieren wir serverseitige Jinja2-Templates mit Tailwind CSS für ein konsistentes Design und Alpine.js für leichte Interaktivität.  
> Als Datenbank verwenden wir MongoDB, weil sich unsere Produktdaten je nach Kategorie stark unterscheiden und wir mit flexiblen Dokumenten gut arbeiten können.  
> Bei den sonstigen Technologien setzen wir auf wichtige Sicherheitsbausteine wie bcrypt für Passwörter, Flask-Login für Sessions und CSRF-Schutz über Flask-WTF.  
> Für die Performance und Zuverlässigkeit nutzen wir Indizes für die Suche und Transaktionen im Checkout, damit Lagerbestand und Bestellungen konsistent bleiben.“

### Präsentationshilfe: Folie „Warum MongoDB und nicht eine andere Datenbank?“

**Was auf die Folie kann (kurz & klar):**
- **Flexible Produktdaten:** Jede Kategorie (CPU, GPU, Monitor) hat andere technische Attribute. MongoDB erlaubt ein dynamisches `specs`-Feld ohne starres Tabellenschema.
- **Schnelle Entwicklung:** Weniger Schema-Migrationen bei neuen Produkttypen oder zusätzlichen Feldern.
- **Passend zum Datenmodell:** Kombination aus Embedding und Referencing (z. B. `users` mit Adresse eingebettet, `orders`/`reviews` referenziert) ist in MongoDB sehr natürlich.
- **Leistung & Zuverlässigkeit:** Indizes für Suche/Filter und Transaktionen im Checkout für konsistente Bestellungen.

**Was du dazu sagen kannst (Sprechtext):**
> „Wir haben MongoDB gewählt, weil unser Shop stark unterschiedliche Produktdaten hat: Eine Grafikkarte braucht andere Felder als ein Monitor oder Prozessor.  
> Mit MongoDB können wir diese Unterschiede in einem flexiblen Dokumentmodell sauber abbilden, ohne ständig Tabellen umzubauen.  
> Gleichzeitig behalten wir Performance und Datenqualität durch Indizes für die Suche und Transaktionen im Checkout.  
> Ein klassisches relationales Schema wäre möglich, würde bei unserem variablen Produktmodell aber mehr Komplexität verursachen.“

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
