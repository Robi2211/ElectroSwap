# 3 Datenbankoperationen und -architektur

---

## 3.1 Zugriffsberechtigungen: Konzept

### Ziel

Ziel des Berechtigungskonzepts ist es, sicherzustellen, dass:
- nur autorisierte Benutzer auf geschützte Funktionen zugreifen können
- die Datenbank vor unbefugtem Zugriff geschützt ist

Wir haben 2 Ebenen:

---

### Applikationsebene (Rollenbasiert)

Auf Applikationsebene werden Benutzer über Rollen gesteuert.

- Jeder Benutzer besitzt eine Rolle (`customer` oder `admin`)
- Der Zugriff auf bestimmte Routen wird über diese Rolle kontrolliert
- Kritische Funktionen (z. B. Admin-Bereich) sind durch den `@admin_required`-Decorator geschützt

**Berechtigungen:**

| Rolle | Berechtigungen |
|-------|---------------|
| customer | - Produkte ansehen<br>- Warenkorb nutzen<br>- Bestellungen erstellen<br>- Bewertungen schreiben |
| admin | - Alle customer-Rechte<br>- Zugriff auf Admin-Dashboard<br>- Produkte erstellen, bearbeiten, löschen (CRUD)<br>- Bestellungen verwalten |

Die Rolle wird direkt im User-Dokument in MongoDB gespeichert:

```json
{
  "username": "max",
  "email": "max@example.com",
  "role": "customer"
}
```

---

### Datenbankebene (MongoDB-Benutzer)

Zusätzlich wird die Datenbank selbst abgesichert. Es existieren mehrere Datenbankbenutzer mit unterschiedlichen Rechten:

| DB-Benutzer | MongoDB-Rolle | Berechtigung |
|-------------|--------------|-------------|
| electroswap_admin | dbOwner | Vollzugriff inkl. Schema-Änderungen |
| electroswap_app | readWrite | Lesen und Schreiben (wird von der Flask-App verwendet) |
| electroswap_readonly | read | Nur Lesen (für Backups und Reporting) |

---

## 3.2 Zugriffsberechtigung: Umsetzung

### Applikationsebene – Decorator im Code

Der `@admin_required`-Decorator in `app/admin/routes.py` schützt alle Admin-Routen:

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

Alle Admin-Routen sind damit geschützt, z. B.:

```python
@admin_bp.route("/")
@admin_required
def dashboard():
    ...
```

---

### Datenbankebene – MongoDB-Benutzer erstellen

Verbindung als Root-Benutzer:

```bash
mongosh -u root -p RootPass000! --authenticationDatabase admin
```

Datenbankbenutzer anlegen:

```javascript
use electroswap

// Admin-Benutzer (Vollzugriff)
db.createUser({
  user: "electroswap_admin",
  pwd: "AdminPass123!",
  roles: [{ role: "dbOwner", db: "electroswap" }]
})

// App-Benutzer (Lesen + Schreiben)
db.createUser({
  user: "electroswap_app",
  pwd: "AppPass456!",
  roles: [{ role: "readWrite", db: "electroswap" }]
})

// Readonly-Benutzer (nur Lesen)
db.createUser({
  user: "electroswap_readonly",
  pwd: "ReadPass789!",
  roles: [{ role: "read", db: "electroswap" }]
})
```

Benutzer anzeigen und verwalten:

```javascript
// Alle Benutzer anzeigen
db.getUsers()

// Einzelnen Benutzer anzeigen
db.getUser("electroswap_app")

// Passwort ändern
db.changeUserPassword("electroswap_app", "NeuesPasswort!")

// Benutzer löschen
db.dropUser("electroswap_readonly")
```

Als bestimmter Benutzer verbinden:

```bash
# Als App-Benutzer (readWrite)
mongosh "mongodb://electroswap_app:AppPass456!@localhost:27017/electroswap?authSource=electroswap"

# Als Readonly-Benutzer
mongosh "mongodb://electroswap_readonly:ReadPass789!@localhost:27017/electroswap?authSource=electroswap"
```

Applikations-Benutzer (Rollen) verwalten:

```javascript
// Benutzerrolle auf admin setzen
db.users.updateOne(
  { email: "max@example.com" },
  { $set: { role: "admin" } }
)

// Benutzerrolle zurücksetzen
db.users.updateOne(
  { email: "max@example.com" },
  { $set: { role: "customer" } }
)

// Alle Admins anzeigen
db.users.find({ role: "admin" }, { username: 1, email: 1 })
```

---

## 3.3 Backup der DB

Das Backup erfolgt mit dem offiziellen MongoDB-Tool `mongodump`. Als Backup-Benutzer wird `electroswap_readonly` verwendet (Least-Privilege-Prinzip: Backup braucht nur Lesezugriff).

### Backup-Befehl (mit Authentifizierung)

```bash
mongodump \
  --host localhost:27017 \
  --db electroswap \
  --username electroswap_readonly \
  --password ReadPass789! \
  --authenticationDatabase electroswap \
  --out ./backup/dumps/electroswap_$(date +%Y%m%d_%H%M%S)
```

### Backup aus Docker-Container

```bash
docker exec electroswap_mongo mongodump \
  --db electroswap \
  --username electroswap_readonly \
  --password ReadPass789! \
  --authenticationDatabase electroswap \
  --archive \
  | gzip > ./backup/dumps/electroswap_$(date +%Y%m%d_%H%M%S).gz
```

### Backup-Skript

Das Skript `backup/backup.sh` erstellt automatisch einen Dump mit Zeitstempel, komprimiert ihn und bereinigt Backups älter als 7 Tage:

```bash
bash backup/backup.sh
```

**Gesicherte Collections:**

| Collection | Inhalt |
|------------|--------|
| users | Benutzerkonten, Rollen, Adressen |
| products | Produktkatalog mit Spezifikationen |
| baskets | Warenkörbe |
| wishlists | Wunschlisten |
| orders | Bestellhistorie |
| reviews | Produktbewertungen |

---

## 3.4 Restore eines DB-Backups

Der Restore erfolgt mit `mongorestore`. Als Restore-Benutzer wird `electroswap_admin` verwendet, da für `--drop` Vollzugriff benötigt wird.

### Restore-Befehl (mit Authentifizierung)

```bash
mongorestore \
  --host localhost:27017 \
  --db electroswap \
  --username electroswap_admin \
  --password AdminPass123! \
  --authenticationDatabase electroswap \
  --drop \
  ./backup/dumps/electroswap_20260320_120000/electroswap
```

> `--drop` löscht die bestehenden Collections vor dem Wiedereinspielen, damit keine doppelten Daten entstehen.

### Restore aus komprimiertem Archiv (Docker)

```bash
gunzip -c ./backup/dumps/electroswap_20260320_120000.gz \
  | docker exec -i electroswap_mongo mongorestore \
      --db electroswap \
      --username electroswap_admin \
      --password AdminPass123! \
      --authenticationDatabase electroswap \
      --drop \
      --archive
```

### Restore-Skript

Das Skript `backup/restore.sh` entpackt das Archiv, fragt zur Sicherheit nach Bestätigung und stellt die Datenbank wieder her:

```bash
bash backup/restore.sh backup/dumps/electroswap_20260320_120000.tar.gz
```

### Berechtigungen beim Restore

Der Readonly-Benutzer darf keinen Restore durchführen – dies zeigt das Least-Privilege-Prinzip:

```bash
mongorestore \
  --username electroswap_readonly \
  --password ReadPass789! \
  --authenticationDatabase electroswap \
  --drop ./backup/dumps/electroswap/
# → Fehler: not authorized on electroswap to execute command { drop: ... }
```

---

## 3.5 Konzept für horizontale Skalierung

### Problemstellung

Eine einzelne Flask-Instanz bildet einen Single Point of Failure und ist auf die Ressourcen eines einzigen Servers begrenzt. Bei erhöhter Last soll die Applikation ohne Downtime horizontal skaliert werden.

### Architektur

```
                   ┌─────────────┐
     Internet  →   │    Nginx    │  Load Balancer (Port 80)
                   │  Round-Robin│
                   └──────┬──────┘
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │  app1   │ │  app2   │ │  app3   │
        │  :5000  │ │  :5000  │ │  :5000  │
        └────┬────┘ └────┬────┘ └────┬────┘
             └───────────┼───────────┘
                         ▼
                 ┌───────────────┐
                 │    MongoDB    │
                 │    :27017     │
                 └───────────────┘
```

### Replikation

Unter Replikation versteht man das Spiegeln der Daten auf mehrere Knoten (Nodes). MongoDB unterstützt dafür sogenannte Replica Sets:

- Ein Primary-Node nimmt alle Schreiboperationen entgegen
- Secondary-Nodes replizieren die Daten automatisch vom Primary
- Fällt der Primary aus, wählen die Secondary-Nodes automatisch einen neuen Primary (Failover)

### Partitionierung (Sharding)

Bei sehr grossen Datenmengen wird die Datenbank horizontal partitioniert (Sharding):

- Die Daten werden anhand eines Shard-Keys auf mehrere Shard-Nodes aufgeteilt
- Jeder Shard enthält nur einen Teil der gesamten Daten
- Ein Config-Server und Mongos-Router koordinieren die Anfragen

### Multimaster vs. Master-Slave

| Strategie | Beschreibung | Einsatz |
|-----------|-------------|---------|
| Master-Slave | Ein Primary schreibt, Secondary liest | Standard MongoDB Replica Set |
| Multimaster | Mehrere Nodes können schreiben | Komplexer, z. B. bei geografisch verteilten Systemen |

In unserer Demo verwenden wir **Master-Slave** (ein MongoDB-Node, 3 App-Nodes).

### Warum ist horizontale Skalierung möglich?

ElectroSwap ist zustandslos (stateless) auf Applikationsebene:

| Aspekt | Lösung |
|--------|--------|
| Sessions | Signierte Client-seitige Cookies (Flask `SECRET_KEY`) – keine serverseitige Speicherung nötig |
| Datenpersistenz | Alle App-Nodes verbinden sich mit derselben MongoDB-Instanz |
| Dateisystem | Keine lokalen Datei-Uploads – kein geteilter Speicher nötig |

### Nginx Load Balancer (Round-Robin)

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

Jeder neue Request wird reihum an den nächsten App-Node weitergeleitet.

### Einschränkungen der Demo

- MongoDB läuft als Single Node (kein Replica Set) → DB-Ebene nicht redundant
- Alle Nodes laufen auf demselben Host → kein echter Hardware-Ausfall abgedeckt
- Kein HTTPS (für Produktion notwendig)

---

## 3.6 Horizontale Skalierung mit 3 Nodes realisieren

Die Infrastruktur wird mit Docker Compose umgesetzt: 3 Flask-App-Nodes, 1 Nginx Load Balancer und 1 MongoDB-Instanz.

### Infrastruktur starten

```bash
# Im Projektverzeichnis
docker compose up --build

# Im Hintergrund
docker compose up --build -d
```

### Laufende Services anzeigen

```bash
docker compose ps
```

Erwartete Ausgabe:

```
NAME                    STATUS          PORTS
electroswap_nginx       Up              0.0.0.0:80->80/tcp
electroswap_app1        Up              5000/tcp
electroswap_app2        Up              5000/tcp
electroswap_app3        Up              5000/tcp
electroswap_mongo       Up (healthy)    0.0.0.0:27017->27017/tcp
```

### Load Balancing verifizieren

```bash
# 9 Requests senden
for i in $(seq 1 9); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost/; done

# Logs der App-Nodes beobachten – Requests werden auf app1/app2/app3 verteilt
docker compose logs -f app1 app2 app3
```

### Node-Ausfall simulieren

```bash
# app2 stoppen (simulierter Ausfall)
docker compose stop app2

# App bleibt über app1 und app3 erreichbar
curl http://localhost/

# app2 wieder starten
docker compose start app2
```

### Seed-Daten einspielen

```bash
docker exec electroswap_app1 python seed_data.py
```

### Datenbankverbindung der App-Nodes prüfen

```bash
# Verbindungsstring des App-Nodes anzeigen
docker exec electroswap_app1 env | grep MONGO_URI
# → mongodb://electroswap_app:AppPass456!@mongo:27017/electroswap?authSource=electroswap
```

### Infrastruktur beenden

```bash
# Stoppen (Daten bleiben erhalten)
docker compose down

# Kompletter Reset inkl. Volumes
docker compose down -v
```
