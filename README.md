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

## Technologien und Begründung (Word-Format)

**1. Python 3.11 + Flask (Backend)**  
Flask wurde gewählt, weil es ein leichtgewichtiges und gut strukturierbares Web-Framework ist.  
Durch Flask-Blueprints kann die Anwendung in fachliche Module (z. B. Auth, Produkte, Warenkorb, Bestellungen) getrennt werden.  
Python ermöglicht zudem eine schnelle Entwicklung und gute Lesbarkeit des Codes.

**2. MongoDB + PyMongo (Datenhaltung)**  
MongoDB wurde gewählt, weil Produktdaten je nach Kategorie unterschiedliche technische Eigenschaften besitzen.  
Diese variablen Attribute können in MongoDB flexibel über Dokumente und das Feld `specs` gespeichert werden.  
PyMongo bietet dabei eine direkte, performante Anbindung aus Flask.

**3. Jinja2 (Serverseitiges Templating)**  
Jinja2 eignet sich für klassische serverseitige Render-Logik und ist nahtlos in Flask integriert.  
Dynamische Inhalte wie Produktlisten, Detailseiten und Bestellverläufe können dadurch klar und wartbar umgesetzt werden.

**4. Tailwind CSS + Alpine.js (Frontend)**  
Tailwind CSS wurde für ein konsistentes, modernes UI mit schneller Styling-Entwicklung gewählt.  
Alpine.js ergänzt kleine interaktive Funktionen (z. B. UI-Zustände), ohne ein schweres Frontend-Framework einzuführen.

**5. Flask-Login, bcrypt, Flask-WTF (Sicherheit & Benutzerverwaltung)**  
Flask-Login übernimmt Session-Management und Zugriff auf den angemeldeten Benutzer.  
bcrypt schützt Passwörter durch sichere Hashing-Verfahren.  
Flask-WTF schützt Formulare gegen CSRF-Angriffe.

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

## Aufbau der Applikation (Word-Format)

**Architekturansatz**  
Die Applikation folgt einem praxisnahen, Flask-typischen **MVC-nahen Aufbau**:

- **Model (Datenebene):** MongoDB-Dokumente und Zugriffe über PyMongo (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`).
- **Controller (Logik):** Flask-Blueprint-Routen in `app/*/routes.py` verarbeiten Requests, validieren Eingaben und steuern Datenbankoperationen.
- **View (Darstellung):** Jinja2-Templates in `app/templates/**` rendern HTML-Seiten für Benutzer und Admins.

Ergänzend wird das **Application-Factory-Pattern** genutzt (`create_app()` in `app/__init__.py`), wodurch Konfiguration, Extension-Initialisierung und Blueprint-Registrierung zentral und wartbar bleiben.

**Code- und Dateistruktur (Überblick)**  

- `run.py`  
  Einstiegspunkt zum Starten der Anwendung.
- `app/__init__.py`  
  Application Factory, Initialisierung von Flask, MongoDB, Login, CSRF, Indexen und Blueprints.
- `app/models.py`  
  User-Wrapper für Flask-Login und User-Loader.
- `app/auth/routes.py`  
  Registrierung, Login, Logout, Profilverwaltung.
- `app/products/routes.py`  
  Produktkatalog, Filterung, Suche, Produktdetails.
- `app/cart/routes.py`  
  Warenkorb-Funktionen (hinzufügen, ändern, entfernen).
- `app/orders/routes.py`  
  Checkout-Prozess, Bestellungen, Bestellhistorie.
- `app/reviews/routes.py`  
  Bewertungslogik inkl. Verified-Purchase-Prüfung.
- `app/admin/routes.py`  
  Admin-Dashboard sowie Produkt-/Bestellverwaltung.
- `app/templates/`  
  Seitenlayouts und UI-Komponenten (Jinja2 + Tailwind CSS).
- `seed_data.py`  
  Seed-Skript zum Befüllen der Datenbank mit Beispieldaten.

**Begründung für diese Struktur**  
Die modulare Trennung nach fachlichen Bereichen reduziert Komplexität, verbessert Wartbarkeit und erleichtert Teamarbeit.  
Neue Features können als eigener Blueprint ergänzt werden, ohne bestehende Bereiche stark zu beeinflussen.

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

Hinweise: `ObjectId("...")`-Werte sind Platzhalter und müssen durch reale IDs aus Ihrer Datenbank ersetzt werden.  
`password_hash` muss ein echter bcrypt-Hash sein (z. B. in Python erzeugt mit `bcrypt.hashpw(b"your_secure_password_here", bcrypt.gensalt()).decode("utf-8")`).
Der unten stehende Hash ist nur ein Formatbeispiel zur Veranschaulichung und darf nicht unverändert produktiv verwendet werden.

```javascript
// users
db.users.insertOne({
  username: "max",
  email: "max@example.com",
  password_hash: "$2b$12$PLACEHOLDER_",
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
  category: "GPU", // gültige Werte siehe seed_data.py
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
  user_id: ObjectId("000000000000000000000001"), // durch reale user_id ersetzen
  items: [
    { product_id: ObjectId("000000000000000000000101"), quantity: 2 }
  ],
  last_updated: new Date()
})

// wishlists
db.wishlists.insertOne({
  user_id: ObjectId("000000000000000000000002"),
  name: "My Wishlist",
  items: [
    { product_id: ObjectId("000000000000000000000102"), added_at: new Date() }
  ]
})

// orders
db.orders.insertOne({
  user_id: ObjectId("000000000000000000000003"),
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
      product_id: ObjectId("000000000000000000000103"),
      name_at_purchase: "Beispiel Produkt",
      price_at_purchase: 199.90,
      quantity: 2
    }
  ]
})

// reviews
db.reviews.insertOne({
  product_id: ObjectId("000000000000000000000104"),
  user_id: ObjectId("000000000000000000000004"),
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

## Weitere Kompetenzen (optional) – Dokumentation (Word-Format)

**1. Erweiterte Datenbank-Funktionen**

- **Index-Strategie für Performance**  
  In der Collection `products` werden Text- und Feldindizes (u. a. Kategorie, Marke, Preis) genutzt; bei `users` ist E-Mail mit einem Unique-Index versehen (Initialisierung in `app/__init__.py`, `_ensure_indexes`).  
  **Mehrwert:** Schnellere Suche/Filterung und Vermeidung doppelter Benutzerkonten.

- **Transaktionen im Checkout-Prozess**  
  Beim Bestellabschluss werden Bestandsprüfung, Bestandsreduktion, Bestellungserstellung und Warenkorb-Leerung in einer MongoDB-Transaktion ausgeführt.  
  **Mehrwert:** Datenkonsistenz auch bei Fehlern oder konkurrierenden Zugriffen.

- **Snapshot-Prinzip bei Bestellungen**  
  In `orders.order_items` werden `name_at_purchase` und `price_at_purchase` gespeichert.  
  **Mehrwert:** Historische Bestellungen bleiben korrekt, auch wenn sich Produktdaten später ändern.

- **Flexible Produktattribute (`specs`)**  
  Produkte besitzen je Kategorie unterschiedliche technische Felder im Objekt `specs` (heterogene Dokumente).  
  **Mehrwert:** Hohe Flexibilität ohne starres relationales Schema.

**2. Erweiterte Applikations-Funktionen**

- **Wishlist mit Move-to-Cart**  
  Produkte können gemerkt und direkt in den Warenkorb übernommen werden.  
  **Mehrwert:** Verbesserte User Experience und höherer Conversion-Fokus.

- **Verified-Purchase-Reviews**  
  Bewertungen sind an einen verifizierten Kauf gekoppelt (`verified_purchase`).  
  **Mehrwert:** Höhere Qualität und Glaubwürdigkeit von Produktbewertungen.

- **Rollenbasiertes Berechtigungskonzept**  
  Trennung zwischen `customer` und `admin` mit eigenem Admin-Bereich (Produkt-/Bestellverwaltung).  
  **Mehrwert:** Sichere Rechtevergabe und klare Trennung von Kunden- und Verwaltungsfunktionen.

- **Modularer Aufbau über Flask-Blueprints**  
  Die Features sind in fachliche Module (`auth`, `products`, `cart`, `orders`, `reviews`, `admin` usw.) getrennt.  
  **Mehrwert:** Bessere Wartbarkeit, Testbarkeit und Erweiterbarkeit der Anwendung.

## Gesamttext für Abgabe (Word-Format)

Für die Umsetzung dieser Applikation setze ich **Python 3.11 mit Flask** als Backend-Technologie ein, da Flask durch Blueprints eine klare Modulstruktur ermöglicht und gleichzeitig eine schnelle, gut wartbare Entwicklung unterstützt. Für die Datenhaltung verwende ich **MongoDB mit PyMongo**, weil die Produktdaten je nach Kategorie unterschiedliche technische Eigenschaften aufweisen und dadurch ein flexibles Dokumentmodell (insbesondere über das Feld `specs`) sinnvoll ist. Für die Oberfläche nutze ich **Jinja2** für serverseitiges Rendering sowie **Tailwind CSS und Alpine.js** für ein modernes, performantes und dennoch schlankes Frontend. Sicherheit und Benutzerverwaltung werden über **Flask-Login**, **bcrypt** und **Flask-WTF (CSRF-Schutz)** umgesetzt.

Der Aufbau der Applikation folgt einem **MVC-nahen Ansatz**: Die Datenebene wird durch MongoDB-Collections (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`) gebildet, die Logik liegt in den Flask-Controllern pro Blueprint (`app/*/routes.py`) und die Darstellung erfolgt über Jinja2-Templates in `app/templates/**`. Zusätzlich wird das **Application-Factory-Pattern** (`create_app()` in `app/__init__.py`) eingesetzt, damit Konfiguration, Extension-Initialisierung, Index-Erstellung und Blueprint-Registrierung zentral organisiert sind. Die Codebasis ist dadurch klar nach Verantwortlichkeiten getrennt und gut erweiterbar.

Die GUI ist als **professionelles Dark-Theme** umgesetzt und legt Wert auf **Ergonomie und intuitive Bedienung**: klare Navigationsstruktur, konsistente Komponenten, gut lesbare Produktdarstellung, verständliche Formular- und Checkout-Abläufe sowie eine getrennte Admin-Oberfläche für Verwaltungsaufgaben. Für den **Zugriff auf den Quellcode** dient das Repository mit der dokumentierten Projektstruktur (u. a. `app/`, `seed_data.py`, `run.py`, `requirements.txt`), sodass Funktionen und Datenflüsse nachvollziehbar geprüft werden können. **Screenshots** der zentralen Ansichten (Startseite, Katalog, Produktdetail, Warenkorb/Checkout, Admin-Dashboard) werden als visueller Nachweis der Benutzerführung und des Designs verwendet.

Die Applikation ist **voll ausgebaut**: Alle relevanten Entitätsmengen sind modelliert und implementiert (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`), es existieren **Indexe** für Performance und Datenqualität (u. a. Text-/Feldindizes auf Produkten, Unique-Index auf `users.email`), und die Anwendung unterstützt das **Einfügen/Ändern** von Daten über mehrere Funktionsbereiche (z. B. Produktverwaltung, Warenkorb, Bestellungen, Bewertungen). Zudem sind **mehrere Seiten** mit vollständigen User-Flows vorhanden (Authentifizierung, Katalog, Detailseite, Warenkorb, Checkout, Bestellhistorie, Wishlist, Admin). Damit sind sowohl die funktionalen Anforderungen als auch der Anspruch an professionelles Design und intuitive Bedienung erfüllt.

## Separater Teil: Voll ausgebaute Applikation (Word-Format)

Die Applikation ist vollständig ausgebaut und erfüllt die geforderten Kernpunkte: **Alle Entitätsmengen** sind umgesetzt (`users`, `products`, `baskets`, `wishlists`, `orders`, `reviews`) und in der Datenbank produktiv nutzbar. Für Leistung und Datenqualität bestehen **Indexe** (u. a. Produktsuche/Filter über Feld- und Textindexe sowie ein Unique-Index auf `users.email`). Das **Einfügen und Ändern** von Daten ist in mehreren Bereichen implementiert (z. B. Benutzerkonto, Produktverwaltung im Admin-Bereich, Warenkorb-Positionen, Bestellstatus und Bewertungen). Zusätzlich umfasst das System **mehrere Seiten mit durchgängigen Abläufen** (Login/Registrierung, Produktkatalog, Produktdetail, Warenkorb, Checkout, Bestellhistorie, Wishlist, Admin). Insgesamt entspricht die Lösung damit einer professionell nutzbaren, intuitiv bedienbaren Full-Application.

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
