# ElectroSwap - Dokumentation

## 1. Einleitung

ElectroSwap ist eine moderne E-Commerce-Plattform für Computer-Hardware und Elektronik. Diese Dokumentation beschreibt die technische Umsetzung und die Entscheidungen bezüglich der verwendeten Technologien.

## 2. Projektkonzept

### 2.1 Projektidee und Begründung der Wahl der NoSQL-Datenbank

Das Projekt ElectroSwap bietet eine umfassende E-Commerce-Plattform für Computer-Hardware und Elektronikkomponenten. Produkte können für unterschiedliche Hardware-Kategorien (CPU, GPU, SSD, Monitor, RAM, Motherboard, PSU, Case, Cooler, Peripheral) angelegt werden, wobei je nach Kategorie unterschiedliche technische Spezifikationen bestehen. Auch Bestellungen und Warenkörbe können mit verschiedenen Attributen erstellt werden. Aufgrund dieser flexiblen und variierenden Datenstruktur wurde eine NoSQL-Datenbank eingesetzt.

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
