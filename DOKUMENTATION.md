# ElectroSwap - Projektdokumentation

## 2.1 Projektidee und Begründung NoSQL-Datenbank

### Projektidee

**ElectroSwap** ist ein vollständiger Online-Shop für Computer-Hardware, der mit modernen Webtechnologien entwickelt wurde. Das Projekt demonstriert den praktischen Einsatz einer NoSQL-Datenbank (MongoDB) in einem realistischen E-Commerce-Szenario.

#### Kernfunktionalitäten:

1. **Produktkatalog** mit 22 realistischen Hardware-Artikeln aus 10 Kategorien (CPU, GPU, SSD, Monitor, RAM, Motherboard, PSU, Case, Cooler, Peripheral)
2. **Benutzerauthentifizierung** mit sicherer Passwort-Hashing (Werkzeug)
3. **Warenkorb-System** mit Add/Update/Remove-Funktionen
4. **Checkout mit Transaktionslogik** (Lagerbestandsprüfung → Bestellung → Lagerreduzierung → Warenkorb leeren)
5. **Bestellhistorie** mit Snapshot-Prinzip (Produktdaten zum Kaufzeitpunkt)
6. **Bewertungssystem** (nur Käufer können bewerten)
7. **Admin-Dashboard** mit Aggregations-Pipeline für Analysen
8. **Such- und Filterfunktion** nach Name und Kategorie
9. **Responsive Dark Mode UI** mit Bootstrap 5

### Begründung für NoSQL-Datenbank (MongoDB)

Die Entscheidung für MongoDB als NoSQL-Datenbank anstelle eines relationalen Datenbanksystems (wie PostgreSQL oder MySQL) basiert auf mehreren technischen und praktischen Vorteilen, die für ein E-Commerce-Projekt wie ElectroSwap besonders relevant sind:

#### 1. **Flexible Schema-Struktur für heterogene Produktattribute**

**Problem bei relationalen Datenbanken:**
- Computer-Hardware hat je nach Kategorie völlig unterschiedliche Spezifikationen
- Eine CPU hat Attribute wie `socket`, `cores`, `threads`, `clock`, `tdp`
- Eine GPU hat `vram`, `cuda_cores`, `boost_clock`, `bus_width`
- Ein Monitor hat `panel_type`, `resolution`, `refresh_rate`, `response_time`
- In relationalen Datenbanken würde dies entweder zu einer Table mit vielen NULL-Werten (EAV-Problem) oder zu komplexen Tabellenstrukturen mit Joins führen

**Lösung mit MongoDB:**
```json
// CPU-Dokument
{
  "name": "AMD Ryzen 9 7950X",
  "category": "CPU",
  "price": 549.99,
  "specs": {
    "socket": "AM5",
    "cores": 16,
    "threads": 32,
    "clock": "4.5 GHz",
    "tdp": "170W"
  }
}

// GPU-Dokument
{
  "name": "NVIDIA GeForce RTX 4090",
  "category": "GPU",
  "price": 1599.99,
  "specs": {
    "vram": "24 GB GDDR6X",
    "cuda_cores": 16384,
    "boost_clock": "2520 MHz",
    "bus_width": "384-bit"
  }
}
```

Jedes Produkt kann seine eigene Spezifikationsstruktur im `specs`-Feld haben, ohne dass das Schema angepasst werden muss. Dies entspricht der **realen Welt**, wo verschiedene Produkttypen unterschiedliche Eigenschaften haben.

#### 2. **Snapshot-Prinzip für Bestellungen**

**Anforderung:**
- Bei Bestellungen müssen Produktdaten (Name, Preis) zum Zeitpunkt des Kaufs gespeichert werden
- Wenn später der Produktpreis geändert wird, soll die historische Bestellung unverändert bleiben

**Umsetzung mit MongoDB:**
```json
{
  "user_id": ObjectId("..."),
  "items": [
    {
      "product_id": ObjectId("..."),
      "name": "AMD Ryzen 9 7950X",  // Snapshot des Produktnamens
      "price": 549.99,                // Snapshot des Preises
      "quantity": 1,
      "image": "..."
    }
  ],
  "total": 549.99,
  "status": "confirmed",
  "created_at": ISODate("2026-03-13T10:00:00Z")
}
```

In MongoDB können wir die Produktdaten direkt in das Bestelldokument einbetten. Dies vermeidet komplexe Historisierungstabellen, die in relationalen Datenbanken nötig wären.

#### 3. **Performante Aggregation Pipeline**

MongoDB bietet eine leistungsstarke **Aggregation Pipeline**, die komplexe Analysen direkt in der Datenbank durchführt:

```python
# Durchschnittspreis pro Kategorie
pipeline = [
    {"$group": {
        "_id": "$category",
        "avg_price": {"$avg": "$price"},
        "total_products": {"$sum": 1},
        "total_stock": {"$sum": "$stock"}
    }},
    {"$sort": {"_id": 1}}
]
```

Diese Pipeline berechnet in **einer** Abfrage:
- Durchschnittspreis pro Kategorie
- Anzahl der Produkte pro Kategorie
- Gesamtlagerbestand pro Kategorie

In SQL würden hierfür mehrere Subqueries oder komplexe GROUP BY-Statements benötigt.

#### 4. **Natürliche Datenmodellierung mit verschachtelten Strukturen**

**Warenkorb-Struktur:**
```json
{
  "user_id": ObjectId("..."),
  "items": [
    {"product_id": ObjectId("..."), "quantity": 2},
    {"product_id": ObjectId("..."), "quantity": 1}
  ]
}
```

Die Warenkorb-Items sind direkt im Dokument verschachtelt. In relationalen Datenbanken würde dies eine separate `basket_items`-Tabelle mit Foreign Keys erfordern, was zu zusätzlichen JOIN-Operationen führt.

**Review-System mit Lookup:**
MongoDB unterstützt auch relationale Muster durch `$lookup` (ähnlich JOIN), wenn nötig:
```python
pipeline = [
    {"$match": {"product_id": ObjectId(product_id)}},
    {"$lookup": {
        "from": "users",
        "localField": "user_id",
        "foreignField": "_id",
        "as": "user"
    }},
    {"$unwind": "$user"}
]
```

#### 5. **Skalierbarkeit und Entwicklungsgeschwindigkeit**

**Horizontale Skalierung:**
- MongoDB unterstützt Sharding (automatische Datenverteilung auf mehrere Server)
- Ideal für E-Commerce-Plattformen, die wachsen sollen

**Schnelle Iteration:**
- Kein ALTER TABLE bei Schema-Änderungen
- Neue Produktkategorien können ohne Datenbank-Migration hinzugefügt werden
- Python-Integration mit PyMongo ist sehr natürlich und pythonisch

#### 6. **Praktische Vorteile in der Implementierung**

**Indexierung für Performance:**
```python
products_col.create_index("name")
products_col.create_index("category")
```

MongoDB-Indizes sind einfach zu erstellen und bieten exzellente Performance für Suchfunktionen.

**Transaktionslogik:**
Die Checkout-Funktion implementiert eine vollständige Transaktionslogik:
1. Lagerbestand prüfen
2. Bestellung erstellen (mit Snapshot)
3. Lagerbestand reduzieren
4. Warenkorb leeren

Dies funktioniert atomisch mit MongoDB's Update-Operationen.

### Warum das Projekt sinnvoll und gut ist

#### 1. **Realitätsnahe Anwendung**
- Das Projekt bildet einen echten E-Commerce-Use-Case ab
- 22 realistische Hardware-Produkte mit korrekten Spezifikationen
- Vollständiger Kaufprozess von Produktsuche bis zur Bestellung

#### 2. **Best Practices werden demonstriert**
- **Sicherheit:** Passwort-Hashing mit Werkzeug (Criterion 2.5)
- **Datenintegrität:** Snapshot-Prinzip für Bestellungen
- **Performance:** Indexierung auf häufig verwendeten Feldern (Criterion 5.1)
- **Transaktionslogik:** Korrekte Abwicklung des Checkout-Prozesses (Criterion 5.2)

#### 3. **Zeigt NoSQL-Stärken**
- **Heterogene Attribute:** Unterschiedliche Specs pro Produktkategorie (Criterion 2.7)
- **Aggregation Pipeline:** Komplexe Analysen für Admin-Dashboard (Criterion 2.8)
- **Flexible Datenmodellierung:** Verschachtelte Strukturen für Warenkörbe und Bestellungen

#### 4. **Vollständige Feature-Implementierung**
- Authentifizierung & Authorization (User/Admin-Rollen)
- CRUD-Operationen (Create, Read, Update, Delete)
- Such- und Filterfunktionen
- Review-System mit Kaufverifizierung
- Admin-Dashboard mit Analytics

#### 5. **Moderne Architektur**
- **Backend:** Flask (Python) mit Blueprint-Struktur
- **Datenbank:** MongoDB mit PyMongo
- **Frontend:** Bootstrap 5 mit responsivem Design
- **Session-Management:** Flask Sessions für Authentifizierung

#### 6. **Lernwert**
Das Projekt eignet sich hervorragend für Lehrzwecke, da es:
- Den praktischen Einsatz von NoSQL-Datenbanken zeigt
- Typische E-Commerce-Herausforderungen löst
- Best Practices für Webentwicklung demonstriert
- Klare Code-Struktur mit Kommentaren zu den Kriterien hat

### Fazit

ElectroSwap ist ein gut durchdachtes Projekt, das die **Vorteile von NoSQL-Datenbanken** in einem realistischen Szenario demonstriert. Die flexible Schema-Struktur von MongoDB ermöglicht es, heterogene Produktdaten natürlich zu modellieren, ohne auf komplexe relationale Strukturen zurückgreifen zu müssen. Die Implementierung zeigt Best Practices für:

- Sichere Benutzerauthentifizierung
- Effiziente Datenmodellierung
- Performante Aggregationsabfragen
- Korrekte Transaktionslogik

Das Projekt ist **sinnvoll**, weil es einen echten Use-Case löst, **gut**, weil es Best Practices folgt, und **lehrreich**, weil es die Stärken von NoSQL-Datenbanken klar aufzeigt.
