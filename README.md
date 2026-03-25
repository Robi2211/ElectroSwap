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
   **Warum dieser Screenshot wichtig ist:** Er zeigt den ersten Eindruck der Plattform (Branding, Farbstimmung, Typografie, Navigation).  
   **Was du in der Doku dazu schreiben kannst:** „Die Startseite setzt mit Dark-Theme, klarer Headline und prägnantem CTA den visuellen Rahmen der Applikation. Bereits im ersten Screen sind Orientierung, Markenbild und Bedienpfad erkennbar.“

2. **Produktübersicht mit Filtern/Suche**  
   **Warum dieser Screenshot wichtig ist:** Hier wird Ergonomie sichtbar, weil User viele Produkte schnell eingrenzen können.  
   **Was du in der Doku dazu schreiben kannst:** „Die Katalogseite priorisiert effiziente Produktsuche durch Filter, Sortierung und Suchfunktion. Dadurch werden kognitive Last und Klickwege reduziert, besonders bei grossen Produktmengen.“

3. **Produktdetailseite**  
   **Warum dieser Screenshot wichtig ist:** Er belegt, dass Informationen strukturiert und entscheidungsrelevant aufbereitet sind (Preis, Spezifikationen, Verfügbarkeit, Bewertung, Kaufaktion).  
   **Was du in der Doku dazu schreiben kannst:** „Die Produktdetailseite bündelt alle kaufrelevanten Informationen in klar getrennten Bereichen. Der Nutzer kann technische Daten vergleichen, Reviews einsehen und den Kauf direkt mit einem primären CTA auslösen.“

4. **Warenkorb + Checkout-Schritt**  
   **Warum dieser Screenshot wichtig ist:** Er zeigt die User Journey vom Produkt bis zur Bestellung.  
   **Was du in der Doku dazu schreiben kannst:** „Der Checkout-Prozess folgt einer logischen Reihenfolge mit klarer Handlungsführung. Mengen, Preise und Zwischensummen sind transparent, wodurch Fehlkäufe reduziert werden.“

5. **Login/Registrierung**  
   **Warum dieser Screenshot wichtig ist:** Er zeigt Formular-Ergonomie und Vertrauen (klare Labels, Fokuszustände, verständliche Eingabeaufforderung).  
   **Was du in der Doku dazu schreiben kannst:** „Die Authentifizierungsseiten sind minimalistisch und fokussieren auf schnelle Dateneingabe. Einheitliche Eingabefelder und hohe Kontraste unterstützen eine fehlerarme Bedienung.“

6. **Admin-Dashboard (optional)**  
   **Warum dieser Screenshot wichtig ist:** Er zeigt, dass das Design nicht nur im Shop, sondern auch im Backoffice konsistent umgesetzt ist.  
   **Was du in der Doku dazu schreiben kannst:** „Auch im Administrationsbereich bleiben Farb- und Interaktionskonzept konsistent. Kennzahlen und Aktionen sind priorisiert dargestellt, was die operative Pflege vereinfacht.“

### So wirken die Screenshots nicht „random“

- Gib jedem Bild eine **funktionale Überschrift** (z. B. „Produktdetail: Kaufentscheidung unterstützen“ statt nur „Screenshot 3“).
- Ergänze pro Bild **2–3 Sätze Analyse**: *Was sieht man? Warum ist es ergonomisch sinnvoll? Welches Ziel wird unterstützt?*
- Verweise bei jedem Bild kurz auf ein GUI-Prinzip (z. B. **Konsistenz**, **visuelle Hierarchie**, **Feedback**, **Effizienz**).
- Nutze eine feste Struktur in der Doku: **Abbildung → Beobachtung → Begründung → Nutzen für User**.

Tipp: Wenn nur 2–3 Screenshots möglich sind, nimm **Startseite**, **Produktübersicht** und **Produktdetailseite** – diese drei zeigen zusammen Branding, Navigation und Kaufprozess am besten.
