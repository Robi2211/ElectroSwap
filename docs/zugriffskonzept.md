# Zugriffskonzept – ElectroSwap

> **Projekt:** ElectroSwap – Premium Hardware E-Commerce
> **Stack:** Python / Flask · MongoDB 7.0 · Nginx · Docker
> **Datum:** 2026-03-21

---

## Übersicht

ElectroSwap sichert den Datenzugriff auf **zwei unabhängigen Ebenen**:

```
┌─────────────────────────────────────────────────────┐
│               Ebene 1: Applikation                  │
│    Rollen: customer / admin                         │
│    Schutz: @login_required + @admin_required        │
├─────────────────────────────────────────────────────┤
│               Ebene 2: Datenbank                    │
│    MongoDB-Benutzer mit SCRAM-SHA-256 Auth          │
│    Rollen: dbOwner / readWrite / read               │
└─────────────────────────────────────────────────────┘
```

Beide Ebenen arbeiten unabhängig: Selbst wenn die Applikation kompromittiert wäre, schützt die Datenbankebene den direkten Zugriff.

---

## Ebene 1: Applikationsrollen (Flask RBAC)

### Rollen

| Rolle | Vergabe | Beschreibung |
|-------|---------|-------------|
| `customer` | Automatisch bei Registrierung | Standardbenutzer |
| `admin` | Manuell durch Datenbankadmin | Erweiterter Zugriff |

### Berechtigungsmatrix

| Funktion | customer | admin |
|----------|:--------:|:-----:|
| Produkte ansehen | ✓ | ✓ |
| Produktsuche / Filter | ✓ | ✓ |
| Warenkorb nutzen | ✓ | ✓ |
| Wunschliste nutzen | ✓ | ✓ |
| Bestellung aufgeben | ✓ | ✓ |
| Bestellhistorie ansehen | ✓ | ✓ |
| Produktbewertungen schreiben | ✓ | ✓ |
| Profil bearbeiten | ✓ | ✓ |
| **Admin-Dashboard** | ✗ | ✓ |
| **Produkte erstellen / bearbeiten / löschen** | ✗ | ✓ |
| **Bestellstatus ändern** | ✗ | ✓ |
| **Alle Benutzer einsehen** | ✗ | ✓ |

### Speicherung im User-Dokument (MongoDB)

```json
{
  "_id": "ObjectId(...)",
  "username": "max",
  "email": "max@example.com",
  "password_hash": "$2b$12$...",
  "role": "customer",
  "address": { ... },
  "created_at": "ISODate(...)"
}
```

### Implementierung im Code

**Decorator `@admin_required`** in `app/admin/routes.py`:

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

**Geschützte Admin-Routen:**

```
GET/POST  /admin/                      → Dashboard
GET       /admin/products              → Produktliste
POST      /admin/products/create       → Produkt erstellen
GET/POST  /admin/products/edit/<id>    → Produkt bearbeiten
POST      /admin/products/delete/<id>  → Produkt löschen
GET       /admin/orders                → Bestellübersicht
POST      /admin/orders/<id>/status    → Status ändern
```

### Passwort-Sicherheit

Passwörter werden mit **bcrypt** gehasht (Salting + Hashing), niemals im Klartext gespeichert:

```python
# Beim Registrieren – Passwort hashen
pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# Beim Login – Passwort prüfen
bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
```

### Demo-Konten

| Rolle | E-Mail | Passwort |
|-------|--------|----------|
| Admin | `admin@electroswap.ch` | `admin123` |
| Customer | `customer@electroswap.ch` | `customer123` |

---

## Ebene 2: Datenbankbenutzer (MongoDB SCRAM-SHA-256)

### Benutzerübersicht

| DB-Benutzer | Rolle | Passwort | Verwendung |
|-------------|-------|----------|-----------|
| `root` | `root` (admin-DB) | `RootPass000!` | MongoDB-Superuser (nur Setup) |
| `electroswap_admin` | `dbOwner` | `AdminPass123!` | Schema-Änderungen, Restore |
| `electroswap_app` | `readWrite` | `AppPass456!` | Flask-Applikation (lesen + schreiben) |
| `electroswap_readonly` | `read` | `ReadPass789!` | Backup, Reporting (nur lesen) |

### Berechtigungsmatrix (Datenbank)

| Operation | root | electroswap_admin | electroswap_app | electroswap_readonly |
|-----------|:----:|:-----------------:|:---------------:|:--------------------:|
| Lesen (find) | ✓ | ✓ | ✓ | ✓ |
| Schreiben (insert/update) | ✓ | ✓ | ✓ | ✗ |
| Löschen (delete) | ✓ | ✓ | ✓ | ✗ |
| Collections erstellen/löschen | ✓ | ✓ | ✗ | ✗ |
| Indexes erstellen | ✓ | ✓ | ✗ | ✗ |
| Backup (mongodump) | ✓ | ✓ | ✗ | ✓ |
| Restore (mongorestore --drop) | ✓ | ✓ | ✗ | ✗ |
| Benutzer verwalten | ✓ | ✓ | ✗ | ✗ |

### Least-Privilege-Prinzip

```
Backup  → electroswap_readonly  (nur Lesen reicht)
App     → electroswap_app       (Lesen + Schreiben)
Restore → electroswap_admin     (--drop braucht Vollzugriff)
Setup   → root                  (nur einmalig bei Installation)
```

### Automatische Erstellung beim Start

Die Benutzer werden beim ersten Start des MongoDB-Containers automatisch durch `mongo-init/init-users.js` angelegt:

```javascript
// electroswap_admin (Vollzugriff)
db.getSiblingDB("electroswap").createUser({
  user: "electroswap_admin",
  pwd: "AdminPass123!",
  roles: [{ role: "dbOwner", db: "electroswap" }]
});

// electroswap_app (Lesen + Schreiben)
db.getSiblingDB("electroswap").createUser({
  user: "electroswap_app",
  pwd: "AppPass456!",
  roles: [{ role: "readWrite", db: "electroswap" }]
});

// electroswap_readonly (nur Lesen)
db.getSiblingDB("electroswap").createUser({
  user: "electroswap_readonly",
  pwd: "ReadPass789!",
  roles: [{ role: "read", db: "electroswap" }]
});
```

---

## Verbindungsbefehle (mongosh)

```bash
# Als Root (nur für Admin-Aufgaben)
docker exec -it electroswap_mongo mongosh \
  -u root -p RootPass000! --authenticationDatabase admin

# Als Admin (Restore, Schema-Änderungen)
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_admin:AdminPass123!@localhost/electroswap?authSource=electroswap"

# Als App-User (Lesen + Schreiben)
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_app:AppPass456!@localhost/electroswap?authSource=electroswap"

# Als Readonly-User (Backup, Reporting)
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_readonly:ReadPass789!@localhost/electroswap?authSource=electroswap"
```

---

## Verwaltungsbefehle

### MongoDB-Benutzer anzeigen

```javascript
// Alle DB-Benutzer anzeigen
use electroswap
db.getUsers()

// Einzelnen Benutzer anzeigen
db.getUser("electroswap_app")
```

### Applikations-Benutzer verwalten

```javascript
// Alle Applikations-User anzeigen
use electroswap
db.users.find({}, { username: 1, email: 1, role: 1, _id: 0 })

// Nur Admins anzeigen
db.users.find({ role: "admin" }, { username: 1, email: 1, _id: 0 })

// Benutzer zum Admin befördern
db.users.updateOne(
  { email: "max@example.com" },
  { $set: { role: "admin" } }
)

// Benutzer wieder auf customer zurücksetzen
db.users.updateOne(
  { email: "max@example.com" },
  { $set: { role: "customer" } }
)
```

### MongoDB-Benutzer verwalten (als Admin)

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

---

## Demo: Berechtigungsunterschiede zeigen

### 1 – Readonly kann nicht schreiben

```bash
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_readonly:ReadPass789!@localhost/electroswap?authSource=electroswap"
```

```javascript
// Lesen funktioniert
db.users.find({}, { username: 1, role: 1 })

// Schreiben schlägt fehl
db.users.insertOne({ test: "unauthorized" })
// → MongoServerError: not authorized on electroswap to execute command { insert: ... }
```

### 2 – Readonly kann nicht restoren

```bash
docker exec electroswap_mongo mongorestore \
  --username electroswap_readonly \
  --password "ReadPass789!" \
  --authenticationDatabase electroswap \
  --db electroswap \
  --drop \
  /dump/irgendein_backup/electroswap
# → Fehler: not authorized on electroswap to execute command { drop: ... }
```

### 3 – App-User kann keine Collections löschen (dropDatabase)

```bash
docker exec -it electroswap_mongo mongosh \
  "mongodb://electroswap_app:AppPass456!@localhost/electroswap?authSource=electroswap"
```

```javascript
// Schreiben funktioniert (readWrite)
db.products.insertOne({ name: "Test" })

// Collection droppen schlägt fehl (kein dbOwner)
db.products.drop()
// → MongoServerError: not authorized on electroswap to execute command { drop: ... }
```

---

## Demo-Skripte (Backup)

| Skript | Zweck | Ergebnis |
|--------|-------|----------|
| `bash demo_backup_fail.sh` | Backup mit **falschem Passwort** | Fehlermeldung: Auth failed |
| `bash demo_backup.sh` | Backup mit **korrektem** Readonly-User | `.gz`-Archiv wird erstellt |
| `bash demo_restore.sh` | Restore mit **Admin-User** | Datenbank wird wiederhergestellt |

---

## Zusammenfassung

```
┌──────────────────────────────────────────────────────────────┐
│  ElectroSwap Zugriffskonzept                                 │
├────────────────────┬─────────────────────────────────────────┤
│  APPLIKATION       │  customer  → normale Nutzung            │
│  (Flask RBAC)      │  admin     → + Admin-Panel / CRUD       │
├────────────────────┼─────────────────────────────────────────┤
│  DATENBANK         │  readonly  → nur lesen (Backup)         │
│  (MongoDB Auth)    │  app       → lesen + schreiben (Flask)  │
│                    │  admin     → Vollzugriff (Restore)      │
│                    │  root      → Superuser (Setup)          │
├────────────────────┼─────────────────────────────────────────┤
│  PRINZIP           │  Least Privilege: jeder Benutzer hat    │
│                    │  nur die minimal nötigen Rechte         │
└────────────────────┴─────────────────────────────────────────┘
```
