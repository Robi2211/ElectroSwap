# 3. Datenbankoperationen und -architektur – ElectroSwap Demo

## 3.1 Konzept für Zugriffsberechtigungen

**MongoDB-Rollen und Benutzer:**
- `electroswap_admin` (Passwort: `AdminPass123!`)
  - Rolle: `dbOwner` – vollständige Kontrolle
  - Darf: Databases/Collections löschen, Benutzer erstellen, Daten ändern

- `electroswap_app` (Passwort: `AppPass456!`)
  - Rolle: `readWrite` – Datenbank lesen/schreiben, keine Admin-Operationen
  - Darf: CRUD-Operationen in electroswap-DB
  - Nutzt die Flask-App

- `electroswap_readonly` (Passwort: `ReadPass789!`)
  - Rolle: `read` – nur Lesezugriff
  - Darf: Nur SELECT/Dump
  - Nutzt Backups und Reporting

**Authentifizierung:** SCRAM-SHA-256 (MongoDB-Standard)

---

## 3.2 Zugriffsberechtigungen zeigen

### Live-Demo: Benutzer & Rollen auflisten
```powershell
# Alle Rollen/Benutzer in electroswap-DB anzeigen
docker exec electroswap_mongo mongosh -u root -p "RootPass000!" --authenticationDatabase admin --eval "db.getSiblingDB('electroswap').getUsers()" --quiet
```

### Live-Demo: readonly-Benutzer darf nicht schreiben
```powershell
# Mit readonly-User versuchen zu schreiben (muss fehlschlagen)
docker exec electroswap_mongo mongosh -u electroswap_readonly -p "ReadPass789!" --authenticationDatabase electroswap --eval "db.getSiblingDB('electroswap').users.insertOne({name: 'hack'})" --quiet
```

### Live-Demo: app-User darf lesen/schreiben
```powershell
# Mit app-User inserting erlaubt
docker exec electroswap_mongo mongosh -u electroswap_app -p "AppPass456!" --authenticationDatabase electroswap --eval "db.getSiblingDB('electroswap').users.countDocuments()" --quiet
```

---

## 3.3 Backup-Konzept

**Strategie:**
- Zeitstempel-basiert: `electroswap_YYYYMMDD_HHMMSS`
- Jedes Backup ist einzigartig → keine Überschreibung
- Wird in `./backup/dumps/` gespeichert (Host-Ordner)
- Docker-Mount: `./backup/dumps:/dump` (Container kann Dumps schreiben)

**Berechtigungen für Backup:**
- Nutzt `electroswap_readonly`-User (Lesezugriff ausreichend)
- Mit `--authenticationDatabase electroswap`

---

## 3.4 Backup und Restore

### Befehl 1: Falsches Passwort (Authentifizierung schlägt fehl)
```powershell
docker exec electroswap_mongo mongodump --db electroswap --username electroswap_readonly --password "FALSCHESPASSWORT" --authenticationDatabase electroswap --out /dump/FAIL_DEMO
```
**Erwartet:** `SCRAM authentication failed`

### Befehl 2: Backup (erfolgreicher Dump)
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\backup\backup.ps1
```

### Befehl 3: Restore (Rollback zu einem Backup)
```powershell
# Finde zuerst einen Backup-Namen:
Get-ChildItem .\backup\dumps -Directory | Select-Object -Last 1 Name

# Danach Restore (mit echtem Backup-Namen):
powershell -NoProfile -ExecutionPolicy Bypass -File .\backup\restore.ps1 -Name <BACKUP_NAME>
```

**Beispiel:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\backup\restore.ps1 -Name electroswap_20260320_151341
```

---

## 3.5 Konzept für horizontale Skalierung

**Docker-Compose Architektur:**
```
┌─────────────────────────────────────────────────────────┐
│                     Nginx Load Balancer                  │
│              (Port 80 / Round-Robin)                     │
└────────────┬────────────┬────────────┬────────────────────┘
             │            │            │
      ┌──────▼──┐  ┌──────▼──┐  ┌──────▼──┐
      │  app1   │  │  app2   │  │  app3   │
      │ :5000   │  │ :5000   │  │ :5000   │
      └──────┬──┘  └──────┬──┘  └──────┬──┘
             │            │            │
             └────────────┼────────────┘
                          │
                     ┌────▼─────┐
                     │ MongoDB   │
                     │:27017     │
                     └───────────┘
                   (Single Instance)
```

**Skalierungsebenen:**
1. **Layer 1: Frontend (Nginx)**
   - Reverse Proxy
   - Load Balancing (Round-Robin)
   - Stateless

2. **Layer 2: Application (3× Flask)** 
   - Horizontale Skalierung: app1, app2, app3
   - Jede Instanz verbindet zu **gleichen** MongoDB
   - Stateless (Sitzungen via Flask-Session/Cookies)
   - Umgebungsvariable: `MONGO_URI=mongodb://electroswap_app:AppPass456!@mongo:27017/electroswap?authSource=electroswap`

3. **Layer 3: Database (MongoDB)**
   - Single-Instance (für diese Demo)
   - Könnte später zu Replica Set erweitert werden

**Horizontal scalierbar, weil:**
- Neue App-Nodes können einfach hinzugefügt werden (docker-compose)
- Nginx verteilt Load automatisch
- Keine Session-Affinität nötig (Cookies sind zustandslos)
- MongoDB ist zentraler Single Point (bei Bedarf Replica Set)

---

## 3.6 Horizontale Skalierung mit 3 Nodes realisieren

### Status der 3 App-Nodes zeigen
```powershell
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | findstr app
```

**Erwartet:**
```
electroswap_app1    Up 30 minutes   5000/tcp
electroswap_app2    Up 30 minutes   5000/tcp
electroswap_app3    Up 30 minutes   5000/tcp
```

### Nginx Load-Balancer Konfiguration zeigen
```powershell
docker exec electroswap_nginx sh -lc "cat /etc/nginx/conf.d/default.conf"
```

### HTTP-Anfrage via Nginx (verteilt auf app1/app2/app3)
```powershell
# 3× anfragen, jede geht zu unterschiedlichem Node
for ($i=1; $i -le 3; $i++) { 
  curl http://localhost/
}
```

### Skalierung live: Weitere Node hinzufügen (Proof-of-Concept)
Falls 4. Node gewünscht: In `docker-compose.yml` `app4` hinzufügen, dann:
```powershell
docker compose up -d app4
docker compose up -d nginx  # nginx neustarten für neue Upstream
```

---

## Demo-Reihenfolge (Live-Präsentation)

1. **Berechtigungen zeigen**
   - `docker exec electroswap_mongo mongosh -u root -p "RootPass000!" --authenticationDatabase admin --eval "db.getSiblingDB('electroswap').getUsers()" --quiet`

2. **readonly-User kann nicht schreiben**
   - `docker exec electroswap_mongo mongosh -u electroswap_readonly -p "ReadPass789!" --authenticationDatabase electroswap --eval "db.getSiblingDB('electroswap').users.insertOne({name: 'hack'})" --quiet`

3. **Falsches Passwort**
   - `docker exec electroswap_mongo mongodump --db electroswap --username electroswap_readonly --password "FALSCH" --authenticationDatabase electroswap --out /dump/FAIL_DEMO`

4. **Backup machen**
   - `powershell -NoProfile -ExecutionPolicy Bypass -File .\backup\backup.ps1`
   - Zeigen neuer Ordner in `backup/dumps`

5. **"Online" Änderung simulieren**
   - Produktname in Compass ändern, oder:
   - `docker exec electroswap_mongo mongosh -u electroswap_app -p "AppPass456!" --authenticationDatabase electroswap --eval "db.getSiblingDB('electroswap').products.updateOne({_id: ObjectId('...')}, {\$set: {name: 'HACKED'}})" --quiet`

6. **Restore (Rollback)**
   - `powershell -NoProfile -ExecutionPolicy Bypass -File .\backup\restore.ps1 -Name electroswap_20260320_XXX`
   - Original-Daten sind wieder da!

7. **3 Nodes zeigen**
   - `docker ps --format "table {{.Names}}\t{{.Status}}" | findstr app`

---

## Weitere Befehle für Dokumentation

### Datenbankgröße
```powershell
docker exec electroswap_mongo mongosh -u electroswap_app -p "AppPass456!" --authenticationDatabase electroswap --eval "db.getSiblingDB('electroswap').stats()" --quiet
```

### Indexes prüfen
```powershell
docker exec electroswap_mongo mongosh -u electroswap_app -p "AppPass456!" --authenticationDatabase electroswap --eval "db.getSiblingDB('electroswap').products.getIndexes()" --quiet
```

### Connection-String für App
```
mongodb://electroswap_app:AppPass456!@mongo:27017/electroswap?authSource=electroswap
```
(Inside Docker)

```
mongodb://electroswap_app:AppPass456!@localhost:27017/electroswap?authSource=electroswap
```
(From Host, für Tools wie Compass)
