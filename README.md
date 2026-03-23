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

## Präsentation (10 Minuten) – Fokus auf fehlende Kriterien 3.2, 3.4, 3.6

Ziel: In 10 Minuten möglichst viele noch offene **Live-Demo-Kriterien** sauber und ohne Hektik zeigen.

### Zeitplan (Vorschlag)

1. **0:00–1:00 – Einstieg & Ziel**
   - Kurzproblem erklären: Warum ElectroSwap + warum NoSQL/MongoDB.
   - Agenda ansagen: **3.2 Rollen**, **3.4 Backup/Restore**, **3.6 horizontale Skalierung**.

2. **1:00–3:30 – Live-Demo 3.2: Zugriffsberechtigungen (Rollen/Benutzer)**
   - In `mongosh` als Admin anmelden.
   - Rollen/Benutzer kurz anzeigen (`show users`, `db.getUsers()`).
   - Mit einem eingeschränkten User anmelden und einen verbotenen Befehl ausführen (Fehler zeigen).
   - Danach mit berechtigtem User denselben Zugriff erfolgreich zeigen.

3. **3:30–6:30 – Live-Demo 3.4: Backup & Restore mit Authentifizierung**
   - `mongodump` mit `--username`, `--password`, `--authenticationDatabase`.
   - Danach Teständerung machen (z. B. 1 Produkt löschen/ändern).
   - Mit `mongorestore --drop` wiederherstellen.
   - Kurz verifizieren: Datensatz ist wieder vorhanden.

4. **6:30–9:00 – Live-Demo 3.6: Horizontale Skalierung mit 3 Nodes**
   - Replika-Set/Cluster-Setup visuell zeigen (3 laufende Nodes/Container).
   - In `mongosh`: `rs.status()` zeigen (PRIMARY + 2 SECONDARY).
   - Optional kurzer Failover: PRIMARY stoppen, neuen PRIMARY anzeigen.
   - Danach kurz ElectroSwap öffnen und zeigen, dass Lesen/Schreiben weiter funktioniert.

5. **9:00–10:00 – Abschluss & Fragen**
   - 3 erreichte Kriterien nochmals 1 Satz je Punkt.
   - Risiken/Limitierungen ehrlich erwähnen (z. B. Demo nur lokal/Container).
   - In Q&A überleiten.

### Konkretes Live-Demo-Drehbuch (zum Üben)

1. **Vorbereitung (vor Präsentationsstart)**
   - App läuft: `python run.py`
   - Daten vorhanden: `python seed_data.py`
   - DB-Instanzen/Container für 3 Nodes bereits gestartet.
   - Terminal-Tabs vorbereitet: **Auth**, **Backup**, **Skalierung**, **App im Browser**.

2. **Teil 3.2 – Rollen**
   - Admin-Login in MongoDB.
   - `use electroswap`
   - Users anzeigen, dann mit Customer-User ein Admin-Kommando testen (soll fehlschlagen).
   - Mit Admin-User dasselbe Kommando erfolgreich ausführen.

3. **Teil 3.4 – Backup/Restore**
   - Backup:
     - `mongodump --db electroswap --out ./backup --username <user> --password --authenticationDatabase admin`
     - Hinweis: Passwort wird interaktiv abgefragt (sicherer, kein Klartext im Befehl).
   - Kontrollierte Änderung:
     - Ein Produkt ändern/löschen.
   - Restore:
     - `mongorestore --db electroswap --drop ./backup/electroswap --username <user> --password --authenticationDatabase admin`
     - Hinweis: Ebenfalls interaktive Passwortabfrage für die Demo einplanen.
   - Prüfen:
     - Produkt ist wieder in Originalzustand.

4. **Teil 3.6 – 3 Nodes**
   - `rs.status()` zeigen.
   - Schreibvorgang (z. B. Produktpreis ändern) durchführen.
   - Wenn möglich PRIMARY kurz stoppen, Wahl eines neuen PRIMARY zeigen, danach erneut Lesezugriff.

### Tipps für eine flüssige Präsentation (6.2)

- Alle Befehle als Copy/Paste vorbereitet haben.
- Demo-Daten vorher fixieren (immer gleiche Produkt-ID verwenden).
- Pro Abschnitt einen „Fallback“ haben (Screenshot oder vorbereitete Ausgabe), falls ein Schritt fehlschlägt.
- Nicht zu viel erklären während Tippen: erst ausführen, dann kurz interpretieren.
