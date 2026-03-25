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

Die Applikation erfüllt 5.5, weil alle geforderten Entitätsmengen vollständig umgesetzt und im laufenden System sichtbar sind. In MongoDB werden die Collections `users`, `products`, `baskets`, `wishlists`, `orders` und `reviews` aktiv verwendet; dadurch sind Benutzerverwaltung, Produktkatalog, Kaufprozess und Bewertungssystem klar voneinander getrennt und gleichzeitig miteinander verknüpft. **Screenshot einfügen:** MongoDB-Ansicht mit allen Collections (z. B. Compass links). **Optionales Video (10–20 Sek.):** kurz durch jede Collection klicken und ein Beispiel-Dokument zeigen.

Zusätzlich sind die relevanten Indexe vorhanden, damit Suche, Filterung und Integrität professionell funktionieren. Konkret gibt es einen Unique-Index auf `users.email`, Filter-Indexe auf `products.category`, `products.brand`, `products.price`, einen Textindex auf `products.name`/`products.description`/`products.brand` sowie die User-bezogenen Indexe für `baskets`, `wishlists` und `orders`. Für Reviews verhindert der Composite-Unique-Index (`product_id`, `user_id`) doppelte Bewertungen pro Nutzer und Produkt. **Screenshot einfügen:** Code-Ausschnitt aus `_ensure_indexes()` in `app/__init__.py`. **Optionales Video (15 Sek.):** im Produktkatalog suchen/filtern und die schnelle Reaktion zeigen.

Das Kriterium „einfügen/ändern“ ist ebenfalls durchgängig erfüllt: Benutzer können sich registrieren und ihre Profiladresse ändern; im Shop können Produkte in den Warenkorb gelegt, Mengen angepasst und Einträge entfernt werden; Wishlist-Einträge lassen sich hinzufügen, entfernen und in den Warenkorb verschieben; beim Checkout wird eine neue Bestellung erzeugt; im Admin-Bereich können Produkte erstellt, bearbeitet und gelöscht werden, und der Bestellstatus kann angepasst werden. **Screenshot einfügen:** (1) Register/Profil, (2) Cart mit Mengenänderung, (3) Admin-Produktformular beim Bearbeiten. **Optionales Video (30–45 Sek.):** kompletter Mini-Flow „Produkt öffnen → in Cart → Checkout → im Admin Status ändern“.

Die Anwendung besteht zudem aus mehreren klar getrennten Seiten und Bereichen: Startseite, Katalog, Produktdetail, Login, Registrierung, Profil, Warenkorb, Wishlist, Checkout, Bestellverlauf sowie Admin-Dashboard mit Produkt- und Bestellverwaltung. Dadurch ist die Applikation nicht nur technisch vollständig, sondern auch als echte, mehrseitige Webanwendung nutzbar. **Screenshot einfügen:** je ein Übersichtsscreenshot aus Customer-Bereich und Admin-Bereich. **Optionales Video (20 Sek.):** Navigation durch Hauptmenü und Admin-Menü.

### 5.6 Professionelles Design und intuitive Bedienung (Voraussetzung 5.5)

Die Anforderung 5.6 ist erfüllt, weil die Oberfläche ein konsistentes und professionelles Erscheinungsbild besitzt. Das User Interface basiert auf einem einheitlichen Dark-Theme mit klarer Farbpalette, wiederkehrenden Komponenten (Karten, Buttons, Formfelder, Meldungen) und einem gemeinsamen Layout über alle Seiten. Dadurch wirkt die Anwendung visuell wie „aus einem Guss“ und nicht wie einzelne, zufällige Unterseiten. **Screenshot einfügen:** Startseite + Produktkatalog nebeneinander, damit man die einheitliche Designsprache direkt sieht. **Optionales Video (10–15 Sek.):** kurzer Wechsel zwischen mehreren Seiten, um die visuelle Konsistenz zu zeigen.

Die Bedienung ist intuitiv, weil Nutzer über die Hauptnavigation sofort zu den wichtigsten Bereichen gelangen und mobile Nutzer ein separates Menü mit denselben Kernfunktionen erhalten. Zusätzlich reduziert die Rollenlogik Komplexität: normale Benutzer sehen Shop-Funktionen, Admins erhalten ergänzend den Verwaltungsbereich. Nach Aktionen wie „Produkt aktualisiert“ oder „Bestellung abgeschlossen“ geben Flash-Meldungen sofort verständliches Feedback. **Screenshot einfügen:** Navigation (Desktop oder Mobile) und eine sichtbare Flash-Meldung nach einer Aktion. **Optionales Video (20–30 Sek.):** Login als User vs. Login als Admin, um unterschiedliche Menüpunkte zu demonstrieren.

Auch die zentralen Benutzerpfade sind ohne Umwege aufgebaut: suchen/filtern im Katalog, Produktdetails ansehen, in Cart oder Wishlist legen, Checkout ausführen und anschließend den Bestellverlauf prüfen. Diese lineare Führung reduziert Fehlbedienung und entspricht dem Verhalten professioneller Shop-Systeme. **Screenshot einfügen:** Sequenz aus 3 Bildern (Katalogfilter → Warenkorb → Bestellverlauf). **Optionales Video (30 Sek.):** kompletter End-to-End-Flow aus Nutzersicht.

### Was wir uns bei 5.5 / 5.6 konkret gedacht haben (für die Doku so formulierbar)

- **Warum „voll ausgebaut“?**  
  Unser Ziel war nicht eine einzelne Demo-Seite, sondern ein kompletter Shop-Flow mit echten Rollen und klarer Trennung zwischen Customer- und Admin-Bereich. Darum haben wir alle zentralen Schritte umgesetzt: Konto erstellen, Produkte finden, kaufen, Bestellung nachverfolgen und als Admin verwalten.

- **Warum genau diese Entitätsmengen?**  
  Die sechs Collections (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`) bilden die realen Verantwortungen eines Shops ab. So bleibt die Datenstruktur verständlich: Produktdaten bleiben im Katalog, Warenkorb/Wishlist sind nutzerbezogen, Bestellungen speichern den Kaufzustand (Snapshot), Reviews sind separat, damit Bewertungen unabhängig vom Produktdatensatz gepflegt werden können.

- **Warum Indexe? Haben wir sie überhaupt?**  
  Ja, wir haben sie implementiert (siehe `app/__init__.py`, Funktion `_ensure_indexes()`). Die Überlegung war: häufige Abfragen (Suche/Filter/Benutzerbezug) müssen schnell sein, und kritische Felder brauchen Integrität. Deshalb:  
  - `users.email` **unique** (kein doppelter Account)  
  - `products.category`, `products.brand`, `products.price` (schnelle Filterung)  
  - Textindex auf `products.name`, `products.description`, `products.brand` (Produktsuche)  
  - `baskets.user_id` **unique**, `wishlists.user_id`, `orders.user_id` (schneller Zugriff pro User)  
  - `reviews(product_id, user_id)` **unique** (ein User bewertet ein Produkt nur einmal)

- **Wie wir die Screenshots begründen (nicht zufällig, sondern mit Aussage):**  
  Jeder Screenshot soll immer direkt zeigen, **welche Anforderung** er belegt.
  1. **Collections-Übersicht (MongoDB Compass):** zeigt, dass alle Entitätsmengen real vorhanden sind.  
  2. **Code `_ensure_indexes()`:** zeigt, dass Indexe technisch definiert sind und nicht nur behauptet werden.  
  3. **Katalog mit Suche/Filter:** zeigt, warum die Produktindexe sinnvoll sind (Anwendungsfall).  
  4. **Admin-Formular (Produkt bearbeiten/löschen):** zeigt „einfügen/ändern“ im Backoffice.  
  5. **Warenkorb mit Mengenänderung + Checkout + Bestellverlauf:** zeigt den vollständigen Mehrseiten-Flow für 5.5.  
  6. **Navigation + Flash-Meldung:** zeigt intuitive Bedienung und direktes Feedback (5.6).
