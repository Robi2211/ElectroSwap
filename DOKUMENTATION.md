# ElectroSwap - Dokumentation

## 1. Einleitung

ElectroSwap ist eine moderne E-Commerce-Plattform für Computer-Hardware und Elektronik. Diese Dokumentation beschreibt die technische Umsetzung und die Entscheidungen bezüglich der verwendeten Technologien.

## 2. Projektkonzept

### 2.1 Projektidee und Begründung der Wahl der NoSQL-Datenbank

Das Projekt ElectroSwap bietet eine umfassende E-Commerce-Plattform für Computer-Hardware und Elektronikkomponenten. Produkte können für unterschiedliche Hardware-Kategorien (CPU, GPU, SSD, Monitor, RAM, Motherboard, PSU, Case, Cooler, Peripheral) angelegt werden, wobei je nach Kategorie unterschiedliche technische Spezifikationen bestehen. Auch Bestellungen und Warenkörbe können mit verschiedenen Attributen erstellt werden. Aufgrund dieser flexiblen und variierenden Datenstruktur wurde eine NoSQL-Datenbank eingesetzt.

### 2.2 Konzeptionelles Datenmodell

Das konzeptionelle Datenmodell von ElectroSwap umfasst sechs Entitätstypen mit ihren jeweiligen Attributen und Beziehungen:

#### Entitätstyp: User (Benutzer)
- username
- email
- password_hash
- role
- address (bestehend aus: street, city, zip_code, country)
- created_at

#### Entitätstyp: Product (Produkt)
- name
- brand
- price
- category
- stock_quantity
- images
- description
- specs (flexible technische Spezifikationen)
- created_at

*Hinweis: Der Entitätstyp Product verfügt über 10 Attribute und erfüllt somit die Anforderung von mindestens 8 Attributen.*

#### Entitätstyp: Basket (Warenkorb)
- user_id
- items (Liste von: product_id, quantity)
- last_updated

#### Entitätstyp: Wishlist (Wunschliste)
- user_id
- name
- items (Liste von: product_id, added_at)

#### Entitätstyp: Order (Bestellung)
- user_id
- order_date
- total_price
- status
- shipping_address (bestehend aus: street, city, zip_code, country)
- order_items (Liste von: product_id, name_at_purchase, price_at_purchase, quantity)

#### Entitätstyp: Review (Bewertung)
- product_id
- user_id
- rating
- comment
- created_at

#### Beziehungen zwischen Entitätstypen

Die folgende Tabelle zeigt die wichtigsten Beziehungen:

| Beziehung | Typ | Beschreibung |
|-----------|-----|--------------|
| User → Basket | 1:1 | Jeder Benutzer hat maximal einen Warenkorb |
| User → Wishlist | 1:N | Ein Benutzer kann mehrere Wunschlisten haben |
| User → Order | 1:N | Ein Benutzer kann mehrere Bestellungen aufgeben |
| User → Review | 1:N | Ein Benutzer kann mehrere Bewertungen schreiben |
| Product → Basket Item | 1:N | Ein Produkt kann in mehreren Warenkörben sein |
| Product → Wishlist Item | 1:N | Ein Produkt kann in mehreren Wunschlisten sein |
| Product → Order Item | 1:N | Ein Produkt kann in mehreren Bestellungen vorkommen |
| Product → Review | 1:N | Ein Produkt kann mehrere Bewertungen haben |

### 2.3 Logisches Datenmodell (NoSQL-Datenmodellierung)

Die Umsetzung des konzeptionellen Datenmodells in MongoDB erfolgt durch sechs Collections. Die Wahl zwischen Embedding und Referencing basiert auf Zugriffsmuster und Datenänderungshäufigkeit.

#### Collection: users

**Strategie:** Embedding für Adressdaten

**Obligatorische Attribute:**
- `_id` (ObjectId) – automatisch generiert
- `username` (String)
- `email` (String) – eindeutig indiziert
- `password_hash` (String)
- `role` (String) – Werte: "customer" oder "admin"
- `created_at` (DateTime)

**Optionale Attribute:**
- `address` (Embedded Document)
  - `street` (String)
  - `city` (String)
  - `zip_code` (String)
  - `country` (String)

**Beispieldokument:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "username": "john_doe",
  "email": "john@electroswap.ch",
  "password_hash": "$2b$12$abcdefghijklmnopqrstuvwxyz...",
  "role": "customer",
  "address": {
    "street": "Hauptstrasse 10",
    "city": "Zurich",
    "zip_code": "8001",
    "country": "Switzerland"
  },
  "created_at": ISODate("2024-01-15T10:30:00Z")
}
```

#### Collection: products

**Strategie:** Heterogene Dokumente mit flexiblem `specs`-Objekt für kategorienspezifische Attribute

**Obligatorische Attribute:**
- `_id` (ObjectId)
- `name` (String)
- `brand` (String) – indiziert
- `price` (Decimal/Number) – indiziert
- `category` (String) – indiziert (CPU, GPU, Monitor, Motherboard, PSU, RAM, Storage, Case, Cooling, Peripherals)
- `stock_quantity` (Integer)
- `created_at` (DateTime)

**Optionale Attribute:**
- `images` (Array of Strings) – URLs zu Produktbildern
- `description` (String) – Volltextindiziert
- `specs` (Embedded Document) – flexible Struktur je nach Kategorie

**Beispieldokument (CPU):**
```json
{
  "_id": ObjectId("507f191e810c19729de860ea"),
  "name": "AMD Ryzen 9 7950X",
  "brand": "AMD",
  "price": 549.00,
  "category": "CPU",
  "stock_quantity": 25,
  "images": ["/static/images/products/ryzen-9-7950x.jpg"],
  "description": "16-core, 32-thread unlocked desktop processor with Zen 4 architecture.",
  "specs": {
    "cores": 16,
    "threads": 32,
    "socket": "AM5",
    "base_clock": "4.5 GHz",
    "boost_clock": "5.7 GHz",
    "tdp": 170,
    "cache": "80 MB"
  },
  "created_at": ISODate("2024-01-10T08:00:00Z")
}
```

**Beispieldokument (GPU):**
```json
{
  "_id": ObjectId("507f191e810c19729de860eb"),
  "name": "NVIDIA GeForce RTX 4090",
  "brand": "NVIDIA",
  "price": 1799.00,
  "category": "GPU",
  "stock_quantity": 10,
  "images": ["/static/images/products/rtx-4090.jpg"],
  "description": "The ultimate GPU for gamers and creators.",
  "specs": {
    "chipset": "AD102",
    "memory": "24 GB GDDR6X",
    "boost_clock": "2520 MHz",
    "cuda_cores": 16384,
    "tdp": 450,
    "interface": "PCIe 4.0 x16"
  },
  "created_at": ISODate("2024-01-10T08:15:00Z")
}
```

#### Collection: baskets

**Strategie:** Referencing für Produkte (schnelle Updates, verhindert Duplikation)

**Obligatorische Attribute:**
- `_id` (ObjectId)
- `user_id` (ObjectId) – Referenz zu users, eindeutig indiziert
- `items` (Array of Embedded Documents)
  - `product_id` (ObjectId) – Referenz zu products
  - `quantity` (Integer)
- `last_updated` (DateTime)

**Beispieldokument:**
```json
{
  "_id": ObjectId("507f191e810c19729de860ec"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "items": [
    {
      "product_id": ObjectId("507f191e810c19729de860ea"),
      "quantity": 1
    },
    {
      "product_id": ObjectId("507f191e810c19729de860eb"),
      "quantity": 2
    }
  ],
  "last_updated": ISODate("2024-01-20T14:30:00Z")
}
```

#### Collection: wishlists

**Strategie:** Referencing für Produkte

**Obligatorische Attribute:**
- `_id` (ObjectId)
- `user_id` (ObjectId) – Referenz zu users, indiziert
- `items` (Array of Embedded Documents)
  - `product_id` (ObjectId) – Referenz zu products
  - `added_at` (DateTime)

**Optionale Attribute:**
- `name` (String) – Name der Wunschliste

**Beispieldokument:**
```json
{
  "_id": ObjectId("507f191e810c19729de860ed"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "My Wishlist",
  "items": [
    {
      "product_id": ObjectId("507f191e810c19729de860ea"),
      "added_at": ISODate("2024-01-18T10:00:00Z")
    },
    {
      "product_id": ObjectId("507f191e810c19729de860eb"),
      "added_at": ISODate("2024-01-19T15:30:00Z")
    }
  ]
}
```

#### Collection: orders

**Strategie:** Snapshot-Prinzip – Produktdaten werden zum Bestellzeitpunkt gespeichert

**Obligatorische Attribute:**
- `_id` (ObjectId)
- `user_id` (ObjectId) – Referenz zu users, indiziert
- `order_date` (DateTime)
- `total_price` (Decimal/Number)
- `status` (String) – z.B. "confirmed", "shipped", "delivered"
- `shipping_address` (Embedded Document)
  - `street` (String)
  - `city` (String)
  - `zip_code` (String)
  - `country` (String)
- `order_items` (Array of Embedded Documents)
  - `product_id` (ObjectId) – Referenz zu products
  - `name_at_purchase` (String) – Produktname zum Bestellzeitpunkt
  - `price_at_purchase` (Decimal/Number) – Preis zum Bestellzeitpunkt
  - `quantity` (Integer)

**Beispieldokument:**
```json
{
  "_id": ObjectId("507f191e810c19729de860ee"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "order_date": ISODate("2024-01-20T16:00:00Z"),
  "total_price": 2897.00,
  "status": "confirmed",
  "shipping_address": {
    "street": "Hauptstrasse 10",
    "city": "Zurich",
    "zip_code": "8001",
    "country": "Switzerland"
  },
  "order_items": [
    {
      "product_id": ObjectId("507f191e810c19729de860ea"),
      "name_at_purchase": "AMD Ryzen 9 7950X",
      "price_at_purchase": 549.00,
      "quantity": 1
    },
    {
      "product_id": ObjectId("507f191e810c19729de860eb"),
      "name_at_purchase": "NVIDIA GeForce RTX 4090",
      "price_at_purchase": 1799.00,
      "quantity": 1
    }
  ]
}
```

#### Collection: reviews

**Strategie:** Referencing für Produkte und Benutzer

**Obligatorische Attribute:**
- `_id` (ObjectId)
- `product_id` (ObjectId) – Referenz zu products, indiziert
- `user_id` (ObjectId) – Referenz zu users
- `rating` (Integer) – Wert zwischen 1 und 5
- `created_at` (DateTime)

**Optionale Attribute:**
- `comment` (String) – Textbewertung

**Beispieldokument:**
```json
{
  "_id": ObjectId("507f191e810c19729de860ef"),
  "product_id": ObjectId("507f191e810c19729de860ea"),
  "user_id": ObjectId("507f1f77bcf86cd799439011"),
  "rating": 5,
  "comment": "Excellent build quality and performance. Exactly as described.",
  "created_at": ISODate("2024-01-21T09:00:00Z")
}
```

#### Designentscheidungen

**Embedding vs. Referencing:**

| Collection | Strategie | Begründung |
|-----------|-----------|------------|
| users | Embedding für address | Adresse wird immer mit Benutzer abgerufen; geringe Update-Frequenz |
| products | Heterogene Dokumente | Unterschiedliche Spezifikationen pro Kategorie; flexible Schema-Struktur |
| baskets | Referencing | Produkte können sich ändern (Preis, Stock); verhindert Daten-Duplikation |
| wishlists | Referencing | Gleiche Gründe wie baskets |
| orders | Snapshot-Prinzip | Historische Bestelldaten müssen unveränderlich bleiben; Preise/Namen zum Kaufzeitpunkt |
| reviews | Referencing | Mehrere Reviews pro Produkt; normalisierte Struktur |

## 3. Datenmodellierung

### 3.1 Übersicht der Collections

ElectroSwap verwendet 6 MongoDB-Collections:

| Collection | Zweck | Strategie |
|-----------|-------|-----------|
| `users` | Benutzerkonten mit eingebetteter Adresse | Embedding |
| `products` | Produktkatalog mit flexiblem `specs`-Objekt | Heterogene Dokumente |
| `baskets` | Warenkörbe mit Produktreferenzen | Referencing |
| `wishlists` | Wunschlisten mit Produktreferenzen | Referencing |
| `orders` | Bestellhistorie mit Snapshot-Daten | Snapshot-Prinzip |
| `reviews` | Produktbewertungen (verifizierte Käufer) | Referencing |

### 3.2 Indexierung

Für optimale Performance werden folgende Indizes verwendet:
- **users**: Eindeutiger Index auf `email`
- **products**: Text-Index auf `name` und `description`, Index auf `category`, `brand`, `price`
- **baskets**: Index auf `user_id`
- **wishlists**: Index auf `user_id`
- **orders**: Index auf `user_id`, `created_at`
- **reviews**: Index auf `product_id`, zusammengesetzter Index auf `user_id` + `product_id`

## 4. Technische Implementierung

### 4.1 Architektur

Die Anwendung folgt dem **Flask Blueprint**-Muster mit folgenden Modulen:
- `auth` - Authentifizierung und Benutzerverwaltung
- `main` - Startseite
- `products` - Produktkatalog und Detailansichten
- `cart` - Warenkorbverwaltung
- `wishlist` - Wunschlistenverwaltung
- `orders` - Bestellabwicklung und Historie
- `reviews` - Bewertungssystem
- `admin` - Administrationsbereich

### 4.2 Sicherheit

- **Passwort-Hashing** mit bcrypt
- **CSRF-Schutz** durch Flask-WTF
- **Session-Management** mit Flask-Login
- **Rollenbasierte Zugriffskontrolle** (RBAC)

### 4.3 MongoDB-Transaktionen

Kritische Operationen wie die Bestellabwicklung nutzen MongoDB-Transaktionen:
```python
with session.start_transaction():
    # Atomare Operationen
    verify_stock()
    reduce_stock()
    create_order()
    clear_basket()
```

## 5. Fazit

ElectroSwap demonstriert erfolgreich den Einsatz einer NoSQL-Datenbank (MongoDB) in einem modernen E-Commerce-Kontext. Die dokumentenorientierte Struktur ermöglicht flexible Produktdaten, effiziente Abfragen und eine saubere Architektur, die sich für die spezifischen Anforderungen eines Hardware-Shops eignet.
