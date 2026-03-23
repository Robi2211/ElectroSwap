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

## Präsentation (10 Minuten) – inkl. Applikationsdemo + fehlende Kriterien 3.2, 3.4, 3.6

Ziel: In 10 Minuten die **Applikation sichtbar zeigen** und gleichzeitig die noch offenen **Live-Demo-Kriterien** sauber abdecken.

### Zeitplan (Vorschlag)

1. **0:00–1:00 – Einstieg & Ziel**
   - Kurzproblem erklären: Warum ElectroSwap + warum NoSQL/MongoDB.
   - Agenda ansagen: **App-Flow**, **3.2 Rollen**, **3.4 Backup/Restore**, **3.6 horizontale Skalierung**.

2. **1:00–4:00 – Live-Demo Applikation (Customer-Flow)**
   - Login als Customer, danach Katalog mit Filter/Suche kurz zeigen.
   - Produktdetail öffnen und dynamische `specs` (unterschiedliche Attribute je Kategorie) zeigen.
   - Produkt in Wishlist/Cart legen und Menge ändern.
   - Optional: Checkout starten und Orders-History kurz zeigen.

3. **4:00–5:00 – Live-Demo Applikation (Admin-Flow)**
   - Login als Admin und Admin Panel öffnen.
   - Kurz Produkt- oder Bestellstatusänderung zeigen.
   - Damit den Unterschied Customer/Admin sichtbar machen.

4. **5:00–6:30 – Live-Demo 3.2: Zugriffsberechtigungen (Rollen/Benutzer)**
   - In `mongosh` als Admin anmelden.
   - Rollen/Benutzer kurz anzeigen (`show users`, `db.getUsers()`).
   - Mit einem eingeschränkten User anmelden und einen verbotenen Befehl ausführen (Fehler zeigen).
   - Danach mit berechtigtem User denselben Zugriff erfolgreich zeigen.

5. **6:30–8:00 – Live-Demo 3.4: Backup & Restore mit Authentifizierung**
   - `mongodump` mit `--username`, `--password`, `--authenticationDatabase`.
   - Danach Teständerung machen (z. B. 1 Produkt löschen/ändern).
   - Mit `mongorestore --drop` wiederherstellen.
   - Kurz verifizieren: Datensatz ist wieder vorhanden.

6. **8:00–9:15 – Live-Demo 3.6: Horizontale Skalierung mit 3 Nodes**
   - Replika-Set/Cluster-Setup visuell zeigen (3 laufende Nodes/Container).
   - In `mongosh`: `rs.status()` zeigen (PRIMARY + 2 SECONDARY).
   - Optional kurzer Failover: PRIMARY stoppen, neuen PRIMARY anzeigen.
   - Danach kurz ElectroSwap öffnen und zeigen, dass Lesen/Schreiben weiter funktioniert.

7. **9:15–10:00 – Abschluss & Fragen**
   - Gezeigte App-Funktionen + 3 erreichte Kriterien nochmals kurz zusammenfassen.
   - Risiken/Limitierungen ehrlich erwähnen (z. B. Demo nur lokal/Container).
   - In Q&A überleiten.

### Konkretes Live-Demo-Drehbuch (zum Üben)

1. **Vorbereitung (vor Präsentationsstart)**
   - App läuft: `python run.py`
   - Daten vorhanden: `python seed_data.py`
   - DB-Instanzen/Container für 3 Nodes bereits gestartet.
   - Terminal-Tabs vorbereitet: **Auth**, **Backup**, **Skalierung**, **App im Browser**.

2. **Teil Applikation – Customer/Admin**
   - Customer einloggen, Produkt suchen, Detailseite mit `specs` zeigen.
   - Wishlist/Cart Aktion durchführen.
   - Admin einloggen und Admin Panel kurz zeigen (Rollenunterschied sichtbar).

3. **Teil 3.2 – Rollen**
   - Admin-Login in MongoDB.
   - `use electroswap`
   - Users anzeigen, dann mit Customer-User ein Admin-Kommando testen (soll fehlschlagen).
   - Mit Admin-User dasselbe Kommando erfolgreich ausführen.

4. **Teil 3.4 – Backup/Restore**
   - Backup:
      - `mongodump --db electroswap --out ./backup --username <USERNAME> --password --authenticationDatabase admin`
      - Hinweis: `<USERNAME>` durch euren DB-Benutzer ersetzen; Passwort wird interaktiv abgefragt (sicherer, kein Klartext im Befehl).
   - Kontrollierte Änderung:
     - Ein Produkt ändern/löschen.
   - Restore:
      - `mongorestore --db electroswap --drop ./backup/electroswap --username <USERNAME> --password --authenticationDatabase admin`
      - Hinweis: `<USERNAME>` ersetzen; ebenfalls interaktive Passwortabfrage für die Demo einplanen.
   - Prüfen:
     - Produkt ist wieder in Originalzustand.

5. **Teil 3.6 – 3 Nodes**
   - `rs.status()` zeigen.
   - Schreibvorgang (z. B. Produktpreis ändern) durchführen.
   - Wenn möglich PRIMARY kurz stoppen, Wahl eines neuen PRIMARY zeigen, danach erneut Lesezugriff.

### Mehr Inhalt für den Präsentationsteil (ohne zusätzliche Live-Risiken)

- **Architektur in 30 Sekunden:** Flask Blueprints + MongoDB Collections + warum das für euer Projekt passt.
- **NoSQL-Begründung in 30 Sekunden:** flexible Produkt-`specs` je Kategorie statt starrem SQL-Schema.
- **Lessons Learned in 30 Sekunden:** was bei Rollen, Backup und Replika-Set schwierig war und wie ihr es gelöst habt.
- **Takeaway in 30 Sekunden:** Was funktioniert produktiv bereits gut, was wäre der nächste Ausbau.

### Sprechtext (direkt nutzbar in der Präsentation)

**1) Wofür ist ElectroSwap?**
- „ElectroSwap ist ein moderner Hardware-Webshop für PC-Komponenten wie CPU, GPU, RAM und Monitore.“
- „Das Ziel ist ein realistischer E-Commerce-Prozess: von Produktsuche über Warenkorb bis Checkout und Bestellhistorie.“
- „Zusätzlich gibt es einen Admin-Bereich, damit wir auch den operativen Teil eines Shops zeigen können.“

**2) Welches Problem lösen wir?**
- „Viele Hardware-Shops sind unübersichtlich: technische Daten sind schwer vergleichbar und der Kaufprozess ist oft fragmentiert.“
- „Wir lösen das mit klaren Filtern, konsistenten Produktdetails und einem durchgängigen User-Flow.“
- „Gleichzeitig adressieren wir ein Datenproblem: verschiedene Produktkategorien brauchen unterschiedliche Attribute – deshalb ein flexibles NoSQL-Modell mit `specs` pro Kategorie.“

**3) Warum diese Technologien?**
- „**Flask**: leichtgewichtig, klar strukturiert mit Blueprints, schnell für modulare Web-Apps.“
- „**MongoDB/PyMongo**: ideal für heterogene Produktdaten (z. B. CPU- vs. Monitor-Spezifikationen) ohne starre Tabellenmigration.“
- „**Tailwind CSS + Alpine.js**: schnelle, moderne UI-Entwicklung mit wenig Overhead.“
- „**Flask-Login + bcrypt + CSRF**: saubere Authentifizierung und grundlegende Sicherheitsmechanismen.“

**4) Business-/Nutzer-Nutzen in 3 Sätzen**
- „Für Kund:innen: schneller finden, besser vergleichen, einfacher bestellen.“
- „Für Betreiber: Admin-Workflow für Produkte/Bestellungen und bessere Datenpflege.“
- „Für das Projektziel: wir zeigen nicht nur UI, sondern auch Datenmodell, Sicherheit, Backup/Restore und Skalierung end-to-end.“

**5) Starker Abschluss-Satz**
- „ElectroSwap verbindet Benutzerfreundlichkeit im Frontend mit einer robusten MongoDB-Architektur im Backend – genau das wollten wir mit dieser LB2 praktisch beweisen.“

### Klare Folien-Struktur (direkt für PowerPoint/Canva)

**Folie 1 – Begrüssung & Team**
- Projekttitel: **ElectroSwap – Premium Hardware Shop**
- Kurzvorstellung Team (Namen/Rollen)
- 1 Satz Einstieg: „Wir zeigen heute einen modernen Hardware-Shop inkl. Live-Demo und Datenbank-Setup.“

**Folie 2 – Ziel der Arbeit**
- Was wollten wir erreichen?  
  → Einen funktionierenden E-Commerce-Prototyp mit realistischem User-Flow bauen.
- Zusätzliches Ziel: zentrale LB2-Kriterien praktisch und live nachweisen.

**Folie 3 – Problemstellung**
- Hardware-Shops sind oft unübersichtlich und schwer vergleichbar.
- Unterschiedliche Produkttypen brauchen unterschiedliche technische Daten.
- Zusätzlich braucht es im Hintergrund sichere Rollen, Backup und Verfügbarkeit.

**Folie 4 – Unsere Lösung (ElectroSwap)**
- Einheitlicher Shop-Prozess: Suchen → Details → Warenkorb/Wishlist → Checkout.
- Rollenbasiert: Customer- und Admin-Bereich.
- Flexible Produktdaten mit `specs` je Kategorie.

**Folie 5 – Technologien**
- Backend: **Python + Flask (Blueprints)**
- Datenbank: **MongoDB + PyMongo**
- Frontend: **Jinja2 + Tailwind CSS + Alpine.js**
- Sicherheit: **Flask-Login, bcrypt, CSRF**

**Folie 6 – Live-Demo Applikation**
- Customer-Flow kurz zeigen (Suche, Produktdetail, Cart/Wishlist).
- Admin-Flow kurz zeigen (z. B. Produkt-/Bestellverwaltung).
- Wichtig: Rollenunterschied sichtbar machen.

**Folie 7 – Kriterium 3.2 (Rollen/Berechtigungen)**
- User/Rollen anzeigen.
- Verbotene Aktion mit eingeschränktem User (Fehler).
- Selbe Aktion mit Admin (erfolgreich).

**Folie 8 – Kriterium 3.4 (Backup & Restore)**
- `mongodump` mit Authentifizierung.
- Kontrollierte Datenänderung.
- `mongorestore --drop` und Verifikation.

**Folie 9 – Kriterium 3.6 (Horizontale Skalierung)**
- 3 Nodes zeigen (PRIMARY + SECONDARYs).
- `rs.status()` kurz präsentieren.
- Optional: kurzer Failover-Nachweis.

**Folie 10 – Fazit & Ausblick**
- Was funktioniert heute bereits stabil?
- Was haben wir gelernt?
- Nächste Ausbaustufen (z. B. Payments, erweiterte Suche, Monitoring).

### Tipps für eine flüssige Präsentation (6.2)

- Alle Befehle als Copy/Paste vorbereitet haben.
- Demo-Daten vorher fixieren (immer gleiche Produkt-ID verwenden).
- Pro Abschnitt einen „Fallback“ haben (Screenshot oder vorbereitete Ausgabe), falls ein Schritt fehlschlägt.
- Nicht zu viel erklären während Tippen: erst ausführen, dann kurz interpretieren.
