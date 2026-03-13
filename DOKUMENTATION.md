# ElectroSwap - Dokumentation

## 1. Einleitung

ElectroSwap ist eine moderne E-Commerce-Plattform für Computer-Hardware und Elektronik. Diese Dokumentation beschreibt die technische Umsetzung und die Entscheidungen bezüglich der verwendeten Technologien.

## 2. Projektkonzept

### 2.1 Projektidee und Begründung der Wahl der NoSQL-Datenbank

#### 2.1.1 Projektidee

ElectroSwap ist ein vollwertiger Online-Shop für Premium-Hardware-Komponenten, der sich an Technik-Enthusiasten und PC-Bauer richtet. Das Projekt umfasst folgende Kernfunktionalitäten:

**Hauptmerkmale:**
- **Umfangreicher Produktkatalog** mit 10 verschiedenen Hardware-Kategorien (CPU, GPU, SSD, Monitor, RAM, Motherboard, PSU, Case, Cooler, Peripheral)
- **Benutzerauthentifizierung** mit Registrierung, Login und Profilverwaltung
- **Intelligente Produktsuche** mit Volltextsuche, Filterung nach Kategorie, Marke und Preisspanne
- **Warenkorb-System** mit persistenter Speicherung pro Benutzer
- **Wunschliste** zum Speichern interessanter Produkte
- **Bestellabwicklung** mit Transaktionssicherheit und Lagerbestandsverwaltung
- **Bewertungssystem** für verifizierte Käufer
- **Admin-Panel** zur Verwaltung von Produkten, Beständen und Bestellungen
- **Rollenbasierte Zugriffskontrolle** (Kunde vs. Administrator)

Das Projekt wurde mit einem modernen Tech-Stack entwickelt:
- **Backend**: Flask (Python) mit Blueprint-Architektur
- **Frontend**: Tailwind CSS + Alpine.js mit Dark-Theme-Design
- **Datenbank**: MongoDB mit PyMongo-Treiber
- **Authentifizierung**: bcrypt + Flask-Login

#### 2.1.2 Begründung der Wahl der NoSQL-Datenbank (MongoDB)

Die Entscheidung für MongoDB als NoSQL-Datenbank basiert auf mehreren projektspezifischen Anforderungen und Vorteilen:

##### **1. Flexibles Schema für heterogene Produktdaten**

Jede Hardware-Kategorie hat völlig unterschiedliche technische Spezifikationen:
- **CPUs**: Kerne, Threads, Takt, Socket, TDP
- **GPUs**: VRAM, Takt, Stromverbrauch, Anschlüsse
- **RAM**: Kapazität, Geschwindigkeit, Latenz, RGB
- **Monitore**: Auflösung, Bildwiederholrate, Panel-Typ, Reaktionszeit

In einer relationalen Datenbank würde dies entweder zu:
- **Mehreren Tabellen** pro Kategorie führen (komplex und wartungsintensiv)
- **Einer generischen EAV-Struktur** (Entity-Attribute-Value) mit vielen Joins führen (langsam und umständlich)
- **Vielen leeren Feldern** in einer einzigen Tabelle führen (ineffizient)

Mit MongoDB können wir ein **dynamisches `specs`-Objekt** pro Produkt verwenden:
```javascript
{
  "_id": ObjectId("..."),
  "name": "AMD Ryzen 9 7950X",
  "category": "CPU",
  "price": 699.00,
  "specs": {
    "cores": 16,
    "threads": 32,
    "base_clock": "4.5 GHz",
    "socket": "AM5"
  }
}

{
  "_id": ObjectId("..."),
  "name": "Dell UltraSharp U2723DE",
  "category": "Monitor",
  "price": 599.00,
  "specs": {
    "resolution": "2560x1440",
    "refresh_rate": "60 Hz",
    "panel_type": "IPS",
    "size": "27 inch"
  }
}
```

##### **2. Embedded Documents für verwandte Daten**

MongoDB ermöglicht das **Einbetten von Subdokumenten**, was die Anzahl der Abfragen reduziert:

**Benutzerprofil mit eingebetteter Adresse:**
```javascript
{
  "_id": ObjectId("..."),
  "email": "kunde@beispiel.de",
  "password_hash": "...",
  "role": "customer",
  "address": {
    "street": "Musterstraße 123",
    "city": "Zürich",
    "postal_code": "8001",
    "country": "Schweiz"
  }
}
```

Dies ist effizienter als separate `users` und `addresses` Tabellen mit Foreign Keys in SQL.

##### **3. Snapshot-Prinzip für Bestellungen**

Bei Bestellungen speichern wir eine **Momentaufnahme** der Produktdaten zum Kaufzeitpunkt:
```javascript
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("..."),
  "created_at": ISODate("2024-03-13T10:30:00Z"),
  "items": [
    {
      "product_id": ObjectId("..."),
      "name": "AMD Ryzen 9 7950X",  // Snapshot
      "price": 699.00,              // Preis zum Kaufzeitpunkt
      "quantity": 1,
      "image": "/static/images/..."
    }
  ],
  "total": 699.00,
  "status": "processing"
}
```

**Vorteil**: Auch wenn sich Produktnamen oder Preise später ändern, bleiben die Bestelldaten historisch korrekt. In SQL würde dies komplexe Historisierungstabellen oder temporale Datenstrukturen erfordern.

##### **4. Referenzierung für Beziehungen**

Für andere Beziehungen nutzen wir **Referenzen** (ähnlich Foreign Keys):
- **Warenkorb**: Referenziert Produkte per `product_id`
- **Wunschliste**: Referenziert Produkte per `product_id`
- **Bewertungen**: Referenziert Produkte per `product_id` und Benutzer per `user_id`

Dies kombiniert die Flexibilität von MongoDB mit der Datenintegrität relationaler Systeme.

##### **5. Skalierbarkeit und Performance**

MongoDB bietet:
- **Horizontale Skalierung** durch Sharding (wichtig für wachsende Produktkataloge)
- **Effiziente Indizes** für Volltextsuche, Kategorie-Filter, Preisbereiche
- **Aggregation Pipeline** für komplexe Datenanalysen im Admin-Dashboard
- **Native JSON-Unterstützung** für moderne REST APIs

##### **6. Entwicklungsgeschwindigkeit**

MongoDB ermöglicht:
- **Schnelles Prototyping** ohne Schema-Migrationen
- **Einfache Iteration** bei sich ändernden Anforderungen
- **Native Python-Integration** mit PyMongo
- **JSON-basierte Datenstrukturen** die direkt mit Flask-Anwendungen funktionieren

##### **7. Transaktionsunterstützung**

Moderne MongoDB-Versionen unterstützen **ACID-Transaktionen**, die wir für die Bestellabwicklung nutzen:
```python
with session.start_transaction():
    # 1. Lagerbestand prüfen
    # 2. Bestand reduzieren
    # 3. Bestellung erstellen
    # 4. Warenkorb leeren
```

Dies gewährleistet Datenintegrität bei kritischen Operationen.

##### **Fazit**

MongoDB ist die ideale Wahl für ElectroSwap, weil:
1. Produktdaten **heterogen** sind und verschiedene Attribute pro Kategorie haben
2. **Embedded Documents** die Anzahl der Abfragen reduzieren
3. Das **Snapshot-Prinzip** historische Datengenauigkeit gewährleistet
4. Die **flexible Schema-Struktur** schnelle Anpassungen ermöglicht
5. **Performance und Skalierbarkeit** für wachsende E-Commerce-Anforderungen optimal sind

Eine relationale Datenbank würde für diesen Anwendungsfall zu mehr Komplexität, langsameren Abfragen und schwierigerer Wartbarkeit führen.

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
