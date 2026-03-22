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

## Textbaustein für die Dokumentation (Word-Format)

### 4.4 GUI, Design und Ergonomie
Die Benutzeroberfläche von ElectroSwap wurde mit Fokus auf ein modernes, professionelles und zugleich gut lesbares Design umgesetzt. Durch das konsistente Farbschema, klare Abstände, einheitliche Komponenten (Buttons, Karten, Formulare) und verständliche Navigation finden sich Benutzer schnell zurecht. Wichtige Aktionen wie Produktsuche, Filtern, Warenkorb und Checkout sind auf mehreren Seiten logisch angeordnet und mit wenigen Klicks erreichbar.  
Die ergonomische Gestaltung zeigt sich besonders in der klaren Seitenstruktur, den eindeutigen Beschriftungen und der responsiven Darstellung für unterschiedliche Bildschirmgrößen. Dadurch wird die Anwendung intuitiv bedienbar und unterstützt eine effiziente Nutzung ohne lange Einarbeitung.

Screenshot: Startseite mit Navigation, Produktkarten und Such-/Filterbereich  
Screenshot: Produktdetailseite mit strukturierter Informationsdarstellung und klaren Call-to-Action-Elementen  
Screenshot: Warenkorb- und Checkout-Seite mit übersichtlichem Ablauf

### 5.5 Voll ausgebaute Applikation
ElectroSwap erfüllt die Anforderungen an eine voll ausgebaute Applikation, da alle zentralen Entitätsmengen vollständig implementiert sind (z. B. Benutzer, Produkte, Warenkörbe, Wunschlisten, Bestellungen und Bewertungen). Die Datenhaltung ist in MongoDB sauber strukturiert und durch passende Indizes optimiert (u. a. für Suche, Kategorien, Marken, Preis sowie eindeutige Benutzer-E-Mails).  
Zusätzlich sind die notwendigen Funktionen zum Einfügen und Ändern von Daten vorhanden. Benutzer können beispielsweise Kontodaten pflegen, Produkte in Warenkorb und Wunschliste verwalten sowie Bestellungen auslösen. Im Admin-Bereich können Produkte erstellt, bearbeitet und Bestellstatus geändert werden.  
Die Anwendung umfasst mehrere logisch verbundene Seiten (Startseite, Katalog, Produktdetails, Authentifizierung, Profil, Warenkorb, Checkout, Bestellhistorie, Admin-Bereich) und bildet damit einen vollständigen End-to-End-Prozess eines Hardware-Shops ab.

Screenshot: Admin-Bereich mit Produktverwaltung (Einfügen/Ändern)  
Screenshot: Datenfluss vom Produktkatalog über Warenkorb bis zur Bestellung  
Screenshot: Beispielansicht für mindestens drei unterschiedliche Entitätsmengen

### 5.6 Professionelles Design und intuitive Bedienung (Voraussetzung: 5.5)
Aufbauend auf der vollständig ausgebauten Applikation (5.5) erreicht ElectroSwap ein professionelles Gesamterscheinungsbild mit hoher Benutzerfreundlichkeit. Das visuelle Design ist konsistent, hochwertig und funktionsorientiert, sodass Benutzer jederzeit erkennen, wo sie sich befinden und welche Aktionen möglich sind.  
Die intuitive Bedienung wird durch klare Navigationspfade, verständliche Formularführung, gut sichtbare Statusmeldungen und eine konsistente Interaktionslogik sichergestellt. Dadurch werden typische Nutzungsszenarien (Produkt finden, vergleichen, kaufen, verwalten) schnell und mit geringer Fehleranfälligkeit durchgeführt.

Screenshot: Konsistente Gestaltung über mehrere Seiten hinweg (z. B. Startseite, Katalog, Profil/Admin)  
Screenshot: Beispiel einer intuitiven Benutzerführung mit klaren Rückmeldungen (z. B. Flash-Meldung nach Aktion)
