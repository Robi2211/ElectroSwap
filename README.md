# ElectroSwap - Premium Hardware Shop

Full-Stack E-Commerce-Applikation fuer Elektronik und PC-Hardware, entwickelt im Rahmen des Moduls **INF165 - LB2**.

**Stack:** Python/Flask | MongoDB Replica Set (3 Nodes) | Nginx Load Balancer | Docker Compose

---

## Tech Stack

| Schicht       | Technologie                              |
|---------------|------------------------------------------|
| Backend       | Python 3.11 / Flask (Blueprints)         |
| Templating    | Jinja2                                   |
| Frontend      | Tailwind CSS v3 + Alpine.js              |
| Datenbank     | MongoDB 7.0 - Replica Set (3 Nodes)      |
| Auth          | bcrypt + Flask-Login + CSRF-Schutz       |
| Load Balancer | Nginx 1.25 (3 App-Nodes)                 |
| Container     | Docker Compose                           |

---

## Features

- **User-Auth** - Registrierung, Login, Logout, Profil mit Adress-Editor
- **Produktkatalog** - Filter (Kategorie, Marke, Preisrange), Volltextsuche, Sortierung
- **Warenkorb** - Hinzufuegen, Menge aendern, entfernen, persistiert pro User
- **Wunschliste** - Hinzufuegen/entfernen, in den Warenkorb verschieben
- **Checkout** - MongoDB-Transaktion (Stock pruefen, reduzieren, Bestellung anlegen)
- **Bestellhistorie** - Mit Snapshot-Daten (Preis zum Kaufzeitpunkt)
- **Bewertungen** - Nur verifizierte Kaeufer koennen bewerten
- **Admin-Panel** - Produkt-CRUD, Lagerbestand, Bestellstatus, Dashboard
- **Rollenkonzept** - Customer vs. Admin (RBAC)

---

## Architektur

Alle drei Flask-Nodes laufen hinter einem Nginx Load Balancer (Round-Robin).
Die Flask-App verbindet sich mit allen drei MongoDB-Nodes ueber eine Replica-Set-URI.

```
         +------------------------------------------+
         |          Nginx  (Port 8080)              |
         |        Round-Robin Load Balancer         |
         +----------+----------+----------+---------+
                    |          |          |
              +-----+--+  +---+----+  +---+----+
              | app1   |  | app2   |  | app3   |
              | Flask  |  | Flask  |  | Flask  |
              +-----+--+  +---+----+  +---+----+
                    +----------+----------+
                               | MongoDB URI (replicaSet=rs0)
         +---------------------+--------------------+
         |                     |                    |
   +-----+------+    +---------+-----+    +---------+---+
   |  mongo1    |    |   mongo2      |    |  mongo3     |
   | (PRIMARY)  |<-->| (SECONDARY)   |<-->| (SECONDARY) |
   | Port 27017 |    | Port 27018    |    | Port 27019  |
   +------------+    +---------------+    +-------------+
```

- Automatisches Failover: bei Ausfall des Primary wird ein Secondary zum neuen Primary gewaehlt
- readPreference=secondaryPreferred: Leseanfragen werden auf Secondaries verteilt
- Keyfile-Authentifizierung zwischen den Nodes

---

## Schnellstart

### Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (mit Docker Compose)
- Git

### 1. Repository klonen

```bash
git clone https://github.com/Robi2211/ElectroSwap.git
cd ElectroSwap
```

### 2. Erstmaliger Start (neue Volumes)

```bash
docker compose down -v && docker compose up --build
```

> Beim ersten Start werden MongoDB-Nodes initialisiert, das Replica Set konfiguriert und alle App-User angelegt (~60-90 Sek).

### 3. Normaler Start

```bash
docker compose up -d
```

### 4. App aufrufen

Oeffne **http://localhost:8080** im Browser.

### 5. Container stoppen

```bash
docker compose down
```

### Ports

| Dienst      | Port  |
|-------------|-------|
| Nginx (App) | 8080  |
| MongoDB 1   | 27017 |
| MongoDB 2   | 27018 |
| MongoDB 3   | 27019 |

---

## Demo-Daten seeden

```bash
docker exec -it electroswap_app1 python seed_data.py
```

Legt 1000 Produkte, 1001 User, 1000 Baskets/Wishlists/Orders/Reviews an.

---

## Demo-Accounts

| Rolle    | E-Mail                   | Passwort     |
|----------|--------------------------|--------------|
| Admin    | admin@electroswap.ch     | admin123     |
| Customer | customer@electroswap.ch  | customer123  |

---

## Backup und Restore

**Backup erstellen (Linux/WSL):**
```bash
./demo_backup.sh
```

**Backup erstellen (Windows PowerShell):**
```powershell
powershell -File .\backup.ps1
```

**Restore durchfuehren:**
```bash
./demo_restore.sh
```

Backups liegen unter `backup/dumps/` (Format: `electroswap_YYYYMMDD_HHMMSS.gz`).

---

## Demo-Scripts

| Script              | Beschreibung                                       |
|---------------------|----------------------------------------------------|
| `demo_backup.sh`    | Backup erstellen und anzeigen                      |
| `demo_restore.sh`   | Restore aus einem Backup durchfuehren              |
| `demo_replica.sh`   | Replica Set Status und Failover-Demo               |
| `demo_index.sh`     | Index-Performance zeigen (mit/ohne Index)          |
| `demo_rollen.sh`    | Rollen und Berechtigungen demonstrieren            |

```bash
chmod +x demo_*.sh
```

---

## Projektstruktur

```
ElectroSwap/
├── app/
│   ├── __init__.py           # App-Factory, MongoDB-Setup, Indexes
│   ├── models.py             # User-Model (Flask-Login)
│   ├── auth/routes.py        # Register, Login, Logout, Profil
│   ├── main/routes.py        # Homepage
│   ├── products/routes.py    # Katalog, Detail, Suche
│   ├── cart/routes.py        # Warenkorb CRUD
│   ├── wishlist/routes.py    # Wunschliste
│   ├── orders/routes.py      # Checkout (Transaktion), Bestellhistorie
│   ├── reviews/routes.py     # Verifizierte Bewertungen
│   ├── admin/routes.py       # Admin-Panel
│   └── templates/            # Jinja2-Templates (Tailwind CSS)
├── mongo-init/
│   └── init-replica.js       # Replica Set Init + User-Erstellung
├── nginx/
│   └── nginx.conf            # Load-Balancer-Konfiguration
├── backup/                   # Backup-Scripts
├── docker-compose.yml        # Gesamte Infrastruktur (8 Services)
├── Dockerfile                # Flask-App Docker Image
├── seed_data.py              # Datenbank-Seeder (1000 Produkte)
├── run.py                    # App-Einstiegspunkt
└── requirements.txt          # Python-Abhaengigkeiten
```

---

## MongoDB Collections

| Collection  | Zweck                                     | Strategie                       |
|-------------|-------------------------------------------|---------------------------------|
| users       | User-Accounts mit eingebetteter Adresse   | Embedding                       |
| products    | Katalog mit flexiblem specs-Objekt        | Heterogene Dokumente (LB2 4.3)  |
| baskets     | Warenkoerbe mit Produkt-Referenzen        | Referencing                     |
| wishlists   | Wunschlisten mit Produkt-Referenzen       | Referencing                     |
| orders      | Bestellhistorie mit Snapshot-Daten        | Snapshot-Prinzip (LB2 5.2)      |
| reviews     | Produktbewertungen (verifizierte Kaeufer) | Referencing                     |

---

## LB2-Kriterien

| Kriterium | Beschreibung       | Umsetzung                                                     |
|-----------|--------------------|---------------------------------------------------------------|
| 2.3 / 2.4 | Schema-Design      | 6 Collections mit sauber definierter Struktur                 |
| 2.7       | Indexes            | Text-, Kategorie-, Marken-, Preis- und Unique-Email-Index     |
| 3.x       | Zugriffskonzept    | 3 MongoDB-Rollen: root, electroswap_app, electroswap_readonly |
| 4.3       | Dynamische Daten   | Heterogenes specs-Objekt je nach Produktkategorie             |
| 5.1       | Indexes            | _ensure_indexes() in der App-Factory                         |
| 5.2       | Transaktionen      | Checkout mit start_transaction() und Snapshot-Orders          |
| 5.5       | CRUD               | Vollstaendiges CRUD auf allen Collections                     |
| 5.7       | Extra Feature      | Wunschliste + automatisches Replica Set Failover              |

---

## MongoDB-Rollen und Benutzer

| Benutzer               | Passwort       | Rolle     | Berechtigung                        |
|------------------------|----------------|-----------|-------------------------------------|
| root                   | RootPass000!   | root      | Vollzugriff                         |
| electroswap_admin      | AdminPass123!  | dbOwner   | Vollzugriff auf electroswap-DB      |
| electroswap_app        | AppPass456!    | readWrite | CRUD in electroswap-DB (Flask-App)  |
| electroswap_readonly   | ReadPass789!   | read      | Nur Lesezugriff (Backups/Reporting) |
