# Kapitel 3 – Daten, Operationen und Architektur

> **Projekt:** ElectroSwap – Premium Hardware E-Commerce
> **Stack:** Python / Flask · MongoDB 7.0 · Nginx · Docker
> **Datum:** 2026-03-20

---

## 3.1 Konzept für Zugriffsberechtigungen

### 3.1.1 Übersicht

ElectroSwap implementiert Zugriffsberechtigungen auf **zwei Ebenen**:

| Ebene | Mechanismus | Zweck |
|-------|-------------|-------|
| **Applikation** | Rollen-Attribut im User-Dokument + `@admin_required`-Decorator | Schützt Admin-Routen vor normalen Benutzern |
| **Datenbank** | MongoDB-eigene Benutzer mit Rollen | Schützt die Datenbank vor direktem, unberechtigtem Zugriff |

---

### 3.1.2 Applikations-Ebene (Flask RBAC)

#### Rollen

| Rolle | Beschreibung | Zugang |
|-------|-------------|--------|
| `customer` | Standardrolle bei der Registrierung | Produkte ansehen, Warenkorb, Bestellungen, Bewertungen |
| `admin` | Manuell vergeben | Zusätzlich: Admin-Dashboard, Produkt-CRUD, Bestellstatus-Verwaltung |

#### Implementierung

Das Rollen-Attribut wird im MongoDB-Dokument gespeichert:

```json
{
  "_id": ObjectId("..."),
  "username": "max",
  "email": "max@example.com",
  "password_hash": "$2b$12$...",
  "role": "customer"
}
```

Der `@admin_required`-Decorator in `app/admin/routes.py` schützt alle Admin-Endpunkte:

```python
def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash("Access denied.", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return wrapper
```

Geschützte Routen (Beispiele):

```
GET/POST  /admin/                        → Dashboard
GET/POST  /admin/products                → Produktliste
POST      /admin/products/create         → Produkt erstellen
GET/POST  /admin/products/edit/<id>      → Produkt bearbeiten
POST      /admin/products/delete/<id>    → Produkt löschen
GET       /admin/orders                  → Bestellübersicht
POST      /admin/orders/<id>/status      → Bestellstatus ändern
```

#### Passwort-Sicherheit

Passwörter werden mit **bcrypt** (Salting + Hashing) gespeichert – niemals im Klartext:

```python
pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
```

---

### 3.1.3 Datenbank-Ebene (MongoDB-Benutzer)

MongoDB unterstützt eigene Benutzer mit feingranularen Rollen. Die drei Benutzer für ElectroSwap:

| DB-Benutzer | Rolle | Berechtigung |
|-------------|-------|-------------|
| `electroswap_admin` | `dbOwner` | Vollzugriff inkl. Schema-Änderungen |
| `electroswap_app` | `readWrite` | Lesen und Schreiben (für die Flask-App) |
| `electroswap_readonly` | `read` | Nur Lesen (für Backups, Reporting) |

#### MongoDB-Befehle: Benutzer anzeigen

```javascript
// Alle Benutzer der Datenbank anzeigen
use electroswap
db.getUsers()

// Einzelnen Benutzer anzeigen
db.getUser("electroswap_app")
```

#### MongoDB-Befehle: Benutzer erstellen

```javascript
use electroswap

// Admin-Benutzer (dbOwner)
db.createUser({
  user: "electroswap_admin",
  pwd: "AdminPass123!",
  roles: [{ role: "dbOwner", db: "electroswap" }]
})

// App-Benutzer (readWrite)
db.createUser({
  user: "electroswap_app",
  pwd: "AppPass456!",
  roles: [{ role: "readWrite", db: "electroswap" }]
})

// Readonly-Benutzer (read)
db.createUser({
  user: "electroswap_readonly",
  pwd: "ReadPass789!",
  roles: [{ role: "read", db: "electroswap" }]
})
```

#### MongoDB-Befehle: Benutzer verwalten

```javascript
// Passwort ändern
db.changeUserPassword("electroswap_app", "NeuesPasswort!")

// Rolle hinzufügen
db.grantRolesToUser("electroswap_readonly", [
  { role: "read", db: "electroswap" }
])

// Rolle entfernen
db.revokeRolesFromUser("electroswap_readonly", [
  { role: "read", db: "electroswap" }
])

// Benutzer löschen
db.dropUser("electroswap_readonly")
```

#### MongoDB-Befehle: Anmelden als bestimmter Benutzer (Shell)

```bash
# Als App-Benutzer verbinden
mongosh "mongodb://electroswap_app:AppPass456!@localhost:27017/electroswap?authSource=electroswap"

# Als Admin-Benutzer verbinden
mongosh "mongodb://electroswap_admin:AdminPass123!@localhost:27017/electroswap?authSource=electroswap"

# Als Readonly-Benutzer verbinden
mongosh "mongodb://electroswap_readonly:ReadPass789!@localhost:27017/electroswap?authSource=electroswap"
```

#### MongoDB Authentication aktivieren (ohne Docker)

```bash
# mongod.conf – auth aktivieren
security:
  authorization: enabled

# MongoDB neu starten
sudo systemctl restart mongod
```

---

### 3.1.4 Applikations-Benutzer verwalten (mongosh-Befehle)

```javascript
// Alle Applikations-Benutzer anzeigen
use electroswap
db.users.find({}, { username: 1, email: 1, role: 1, created_at: 1 })

// Nur Admins anzeigen
db.users.find({ role: "admin" }, { username: 1, email: 1 })

// Benutzerrolle auf admin setzen
db.users.updateOne(
  { email: "max@example.com" },
  { $set: { role: "admin" } }
)

// Benutzerrolle auf customer zurücksetzen
db.users.updateOne(
  { email: "max@example.com" },
  { $set: { role: "customer" } }
)

// Benutzer löschen
db.users.deleteOne({ email: "spam@example.com" })
```

---

## 3.2 Live-Demo: Zugriffsberechtigungen

> **Demo-Ablauf** – folgende Schritte in dieser Reihenfolge durchführen:

### Schritt 1 – Verschiedene Rollen in der Applikation zeigen

1. Browser öffnen → `http://localhost` (oder `http://localhost:5000` ohne Docker)
2. Als **Customer** einloggen:
   - E-Mail: `customer@electroswap.ch`
   - Passwort: `customer123`
3. Zeigen: Menü enthält **kein** Admin-Link
4. Direktaufruf `http://localhost/admin/` → Weiterleitung mit «Access denied»
5. Ausloggen
6. Als **Admin** einloggen:
   - E-Mail: `admin@electroswap.ch`
   - Passwort: `admin123`
7. Zeigen: Admin-Dashboard zugänglich, Produkte und Bestellungen verwaltbar

### Schritt 2 – MongoDB-Benutzer in der Shell zeigen

```bash
# Im Container (Docker-Setup)
docker exec -it electroswap_mongo mongosh \
  -u root -p RootPass000! --authenticationDatabase admin

# Benutzer anzeigen
use electroswap
db.getUsers()
```

### Schritt 3 – Berechtigungsunterschiede zeigen

```bash
# Als readonly-Benutzer verbinden
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_readonly:ReadPass789!@localhost/electroswap?authSource=electroswap"

# Lesezugriff funktioniert
db.users.find({}, { username: 1, role: 1 })

# Schreibzugriff schlägt fehl (zeigt Berechtigungsfehler)
db.users.insertOne({ test: "unauthorized" })
```

### Schritt 4 – Rolle promoten (live in der Shell)

```javascript
// Benutzer auf Admin befördern
use electroswap
db.users.updateOne(
  { email: "customer@electroswap.ch" },
  { $set: { role: "admin" } }
)

// Zurück zum Browser – nach erneutem Login ist Admin-Bereich zugänglich
```

---

## 3.3 Backup-Konzept

### 3.3.1 Strategie

| Aspekt | Entscheidung | Begründung |
|--------|-------------|-----------|
| **Tool** | `mongodump` / `mongorestore` | Offizielle MongoDB-Tools, BSON-Format |
| **Benutzer** | `electroswap_readonly` | Least-Privilege: Backup braucht nur Lesezugriff |
| **Restore-Benutzer** | `electroswap_admin` | Vollzugriff für `--drop` + Wiedereinspielen |
| **Format** | Komprimiertes Archiv `.tar.gz` | Platzsparend, portabel |
| **Aufbewahrung** | 7 Tage automatische Bereinigung | Ausgewogenes Verhältnis Speicher/Sicherheit |
| **Zeitstempel** | `YYYYMMDD_HHMMSS` im Dateinamen | Eindeutige Identifikation, einfaches Sortieren |

### 3.3.2 Backup-Befehl (manuell)

```bash
# Ohne Authentifizierung (lokale Entwicklung)
mongodump --db electroswap --out ./backup/dumps/

# Mit Authentifizierung (Produktion / Docker)
mongodump \
  --host localhost:27017 \
  --db electroswap \
  --username electroswap_readonly \
  --password ReadPass789! \
  --authenticationDatabase electroswap \
  --out ./backup/dumps/electroswap_$(date +%Y%m%d_%H%M%S)

# Aus laufendem Docker-Container
docker exec electroswap_mongo mongodump \
  --db electroswap \
  --username electroswap_readonly \
  --password ReadPass789! \
  --authenticationDatabase electroswap \
  --archive \
  | gzip > ./backup/dumps/electroswap_$(date +%Y%m%d_%H%M%S).gz
```

### 3.3.3 Restore-Befehl (manuell)

```bash
# Ohne Authentifizierung
mongorestore --db electroswap --drop ./backup/dumps/electroswap/

# Mit Authentifizierung + Drop (überschreibt bestehende Daten)
mongorestore \
  --host localhost:27017 \
  --db electroswap \
  --username electroswap_admin \
  --password AdminPass123! \
  --authenticationDatabase electroswap \
  --drop \
  ./backup/dumps/electroswap_20260320_120000/electroswap

# Aus komprimiertem .gz-Archiv (Docker)
gunzip -c ./backup/dumps/electroswap_20260320_120000.gz \
  | docker exec -i electroswap_mongo mongorestore \
      --db electroswap \
      --username electroswap_admin \
      --password AdminPass123! \
      --authenticationDatabase electroswap \
      --drop \
      --archive
```

### 3.3.4 Backup-Skripte

Automatisierte Skripte sind im Projekt enthalten:

| Datei | Plattform | Funktion |
|-------|-----------|----------|
| `backup/backup.sh` | Linux / Git Bash | Erstellt komprimierten `.gz`-Dump mit Zeitstempel, bereinigt Backups >7 Tage |
| `backup/restore.sh` | Linux / Git Bash | Bestätigt Datenverlust, stellt aus `.gz`-Archiv wieder her |
| `backup.ps1` | Windows (PowerShell) | Erstellt Dump über Volume-Mount, schreibt in `backup/dumps/` |
| `restore.ps1` | Windows (PowerShell) | Restore aus Volume-Mount-Ordner mit Bestätigung |

```bash
# Linux / Git Bash – Backup
bash backup/backup.sh

# Linux / Git Bash – Restore
bash backup/restore.sh backup/dumps/electroswap_20260321_120000.gz
```

```powershell
# Windows PowerShell – Backup
.\backup.ps1

# Windows PowerShell – Restore
.\restore.ps1 -BackupName electroswap_20260321_120000
```

### 3.3.5 Collections im Backup

Alle 6 Collections werden gesichert:

| Collection | Inhalt |
|------------|--------|
| `users` | Benutzerkonten, Rollen, Adressen |
| `products` | Produktkatalog mit Spezifikationen |
| `baskets` | Warenkörbe |
| `wishlists` | Wunschlisten |
| `orders` | Bestellhistorie (Snapshot) |
| `reviews` | Produktbewertungen |

---

## 3.4 Live-Demo: Backup und Restore mit Authentifizierung

> **Demo-Ablauf:**

### Schritt 1 – Aktuellen Zustand zeigen

```bash
# Im MongoDB-Container verbinden
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_admin:AdminPass123!@localhost/electroswap?authSource=electroswap"

# Anzahl Dokumente vor Backup zeigen
db.products.countDocuments()
db.users.countDocuments()
db.orders.countDocuments()
```

### Schritt 2 – Backup erstellen

```bash
# Backup-Skript ausführen
bash backup/backup.sh

# Oder manuell mit mongodump
docker exec electroswap_mongo mongodump \
  --db electroswap \
  --username electroswap_readonly \
  --password ReadPass789! \
  --authenticationDatabase electroswap \
  --archive | gzip > backup/dumps/electroswap_demo.gz

# Archiv anzeigen
ls -lh backup/dumps/
```

### Schritt 3 – Daten verändern (simulierter Datenverlust)

```bash
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_admin:AdminPass123!@localhost/electroswap?authSource=electroswap"
```

```javascript
// Alle Produkte löschen (Datenverlust simulieren)
db.products.deleteMany({})
db.products.countDocuments()  // → 0
```

### Schritt 4 – Restore durchführen

```bash
# Linux / Git Bash
bash backup/restore.sh backup/dumps/electroswap_demo.gz
```

```powershell
# Windows PowerShell
.\restore.ps1 -BackupName electroswap_demo
```

### Schritt 5 – Wiederherstellung verifizieren

```javascript
// Zurück in mongosh
db.products.countDocuments()  // → Originalanzahl
db.products.findOne({}, { name: 1, price: 1 })
```

### Schritt 6 – Berechtigungen zeigen: Readonly kann nicht restoren

```bash
# Readonly-User darf keinen Restore durchführen (--drop erfordert Schreibrecht)
docker exec electroswap_mongo mongorestore \
  --username electroswap_readonly \
  --password "ReadPass789!" \
  --authenticationDatabase electroswap \
  --db electroswap \
  --drop \
  /dump/electroswap_demo/electroswap
# → Fehler: not authorized on electroswap to execute command { drop: ... }
```

---

## 3.5 Konzept für horizontale Skalierung

### 3.5.1 Problemstellung

Eine einzelne Flask-Instanz bildet einen **Single Point of Failure** und ist auf die Ressourcen eines einzigen Servers begrenzt. Bei erhöhter Last (z.B. Sale-Aktionen) soll die Applikation ohne Downtime horizontal skaliert werden.

### 3.5.2 Architekturübersicht

```
                       ┌─────────────┐
         Internet  →   │    Nginx    │  (Load Balancer, Port 80)
                       │  Round-Robin│
                       └──────┬──────┘
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              ┌─────────┐ ┌─────────┐ ┌─────────┐
              │  app1   │ │  app2   │ │  app3   │
              │ :5000   │ │ :5000   │ │ :5000   │
              └────┬────┘ └────┬────┘ └────┬────┘
                   └───────────┼───────────┘
                               ▼
                       ┌───────────────┐
                       │    MongoDB    │
                       │   :27017      │
                       └───────────────┘
```

### 3.5.3 Warum ist horizontale Skalierung möglich?

ElectroSwap ist **zustandslos (stateless)** auf Applikationsebene:

| Aspekt | Lösung | Begründung |
|--------|--------|-----------|
| **Sessions** | Signierte Client-seitige Cookies (Flask `SECRET_KEY`) | Keine serverseitige Session-Speicherung nötig |
| **Persistenter Zustand** | MongoDB (zentral, single node) | Alle App-Nodes lesen/schreiben dieselbe DB |
| **Dateisystem** | Keine lokalen Datei-Uploads | Produkt-Bilder via URL, kein lokaler Speicher |
| **Cache** | Kein app-lokaler Cache | Keine Inkonsistenz zwischen Nodes |

### 3.5.4 Komponenten

| Komponente | Technologie | Funktion |
|-----------|-------------|---------|
| **Load Balancer** | Nginx 1.25 | Verteilt HTTP-Requests Round-Robin auf 3 App-Nodes |
| **App-Nodes** | Flask (3×) in Docker | Verarbeiten Requests unabhängig voneinander |
| **Datenbank** | MongoDB 7.0 | Gemeinsamer, persistenter Datenspeicher |

### 3.5.5 Nginx Load Balancing

Konfiguration in `nginx/nginx.conf`:

```nginx
upstream electroswap_app {
    server app1:5000;
    server app2:5000;
    server app3:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://electroswap_app;
        proxy_set_header Host            $host;
        proxy_set_header X-Real-IP       $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Verteilungsstrategie:** Round-Robin (Standard) – jeder neue Request geht reihum an den nächsten Node.

### 3.5.6 Skalierbarkeit

| Szenario | Massnahme |
|----------|-----------|
| Mehr Last | Weiteren App-Service in `docker-compose.yml` + Nginx-Upstream ergänzen |
| Node fällt aus | Nginx erkennt dies und leitet nur noch an gesunde Nodes weiter |
| DB-Engpass | MongoDB Replica Set oder Sharding einrichten (nächste Stufe) |

### 3.5.7 Einschränkungen der Demo-Architektur

- MongoDB läuft als **Single Node** (kein Replica Set) → Datenbankebene ist nicht redundant
- Alle Nodes laufen auf **demselben Host** → kein echter Hardware-Ausfall abgedeckt
- Kein HTTPS (TLS-Termination bei Nginx für Produktion notwendig)

---

## 3.6 Horizontale Skalierung mit 3 Nodes – Setup & Demo

### 3.6.1 Voraussetzungen

```bash
# Docker und Docker Compose installiert prüfen
docker --version          # Docker 24+
docker compose version    # v2.20+
```

### 3.6.2 Infrastruktur starten

```bash
# Im Projektverzeichnis
cd C:\Projects\ElectroSwap\ElectroSwap

# Images bauen und alle Services starten
docker compose up --build

# Oder im Hintergrund
docker compose up --build -d
```

### 3.6.3 Laufende Services anzeigen

```bash
docker compose ps
```

Erwartete Ausgabe:

```
NAME                    IMAGE              STATUS          PORTS
electroswap_nginx       nginx:1.25-alpine  Up             0.0.0.0:80->80/tcp
electroswap_app1        electroswap-app1   Up             5000/tcp
electroswap_app2        electroswap-app2   Up             5000/tcp
electroswap_app3        electroswap-app3   Up             5000/tcp
electroswap_mongo       mongo:7.0          Up (healthy)   0.0.0.0:27017->27017/tcp
```

### 3.6.4 Load Balancing verifizieren

```bash
# Mehrere Requests senden und Container-Namen in Logs beobachten
for i in $(seq 1 9); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost/; done

# Logs der App-Nodes gleichzeitig beobachten
docker compose logs -f app1 app2 app3
```

Im Log ist erkennbar, dass Requests reihum auf app1, app2 und app3 verteilt werden.

### 3.6.5 Node-Ausfall simulieren

```bash
# app2 stoppen (simulierter Ausfall)
docker compose stop app2

# App bleibt erreichbar über app1 und app3
curl http://localhost/

# app2 wieder starten
docker compose start app2
```

### 3.6.6 Datenbank-Authentifizierung im Stack verifizieren

```bash
# Verbindungsstring der App-Nodes prüfen (readWrite-Benutzer)
docker exec electroswap_app1 env | grep MONGO_URI
# → mongodb://electroswap_app:AppPass456!@mongo:27017/electroswap?authSource=electroswap

# MongoDB-Verbindung direkt testen
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_app:AppPass456!@localhost/electroswap?authSource=electroswap" \
  --eval "db.products.countDocuments()"
```

### 3.6.7 Seed-Daten einspielen

```bash
# Seed-Skript im laufenden Container ausführen
docker exec electroswap_app1 python seed_data.py
```

### 3.6.8 Infrastruktur beenden

```bash
# Stoppen (Daten bleiben im Volume erhalten)
docker compose down

# Stoppen + Volumes löschen (kompletter Reset)
docker compose down -v
```

---

## Zusammenfassung der erstellten Dateien

| Datei | Abschnitt | Zweck |
|-------|-----------|-------|
| `Dockerfile` | 3.6 | Flask-App containerisieren |
| `docker-compose.yml` | 3.6 | 3 App-Nodes + Nginx + MongoDB orchestrieren |
| `nginx/nginx.conf` | 3.5 / 3.6 | Round-Robin Load Balancer |
| `mongo-init/init-users.js` | 3.1 | MongoDB-Benutzer automatisch anlegen |
| `backup/backup.sh` | 3.3 / 3.4 | Automatisiertes Backup mit mongodump |
| `backup/restore.sh` | 3.3 / 3.4 | Restore aus Archiv mit mongorestore |
| `docs/3_daten_und_architektur.md` | 3.1–3.6 | Diese Dokumentation |
