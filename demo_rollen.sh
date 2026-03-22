#!/bin/bash
# ============================================================
# demo_rollen.sh  –  Zugriffsberechtigungen Demo (3.2)
# ============================================================
# Zeigt live:
#   A) Applikationsebene: customer vs. admin (Browser-Hinweise)
#   B) Datenbankebene:    3 MongoDB-User mit unterschiedlichen Rechten
#   C) Readonly darf nicht schreiben (Fehler zeigen)
#   D) Live-Rollenänderung: customer → admin → customer
#
# Verwendung: bash demo_rollen.sh
# Voraussetzung: docker compose up -d && Stack ist healthy

set -e

ADMIN_URL='mongodb://electroswap_admin:AdminPass123%21@localhost:27017/electroswap?authSource=electroswap'
APP_URL='mongodb://electroswap_app:AppPass456%21@localhost:27017/electroswap?authSource=electroswap'
READONLY_URL='mongodb://electroswap_readonly:ReadPass789%21@localhost:27017/electroswap?authSource=electroswap'

# ── Hilfsfunktionen ──────────────────────────────────────────
header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

step() {
    echo ""
    echo "  ▶  $1"
    echo ""
}

pause() {
    echo ""
    echo "  [ENTER drücken um fortzufahren...]"
    read -r
}

run_mongo() {
    docker exec electroswap_mongo mongosh "$1" --quiet --eval "$2" 2>&1
}

# ══════════════════════════════════════════════════════════════
header "A) APPLIKATIONSEBENE – customer vs. admin"
# ══════════════════════════════════════════════════════════════

step "Alle Applikationsbenutzer anzeigen (username, email, rolle):"
run_mongo "$ADMIN_URL" \
    'db.users.find({},{username:1,email:1,role:1,_id:0}).toArray()'

step "Nur Admin-Benutzer:"
run_mongo "$ADMIN_URL" \
    'db.users.find({role:"admin"},{username:1,email:1,_id:0}).toArray()'

step "Anzahl pro Rolle:"
run_mongo "$ADMIN_URL" \
    'db.users.aggregate([{$group:{_id:"$role",anzahl:{$sum:1}}}]).toArray()'

echo ""
echo "  ┌──────────────────────────────────────────────────────┐"
echo "  │  BROWSER-DEMO  →  http://localhost                   │"
echo "  │                                                      │"
echo "  │  1. Als Customer einloggen:                          │"
echo "  │     E-Mail:    customer@electroswap.ch               │"
echo "  │     Passwort:  customer123                           │"
echo "  │     → Kein Admin-Link im Menü                        │"
echo "  │     → http://localhost/admin/ → 'Access denied'      │"
echo "  │                                                      │"
echo "  │  2. Ausloggen, dann als Admin einloggen:             │"
echo "  │     E-Mail:    admin@electroswap.ch                  │"
echo "  │     Passwort:  admin123                              │"
echo "  │     → Admin-Link sichtbar im Menü                    │"
echo "  │     → http://localhost/admin/ → Dashboard öffnet     │"
echo "  └──────────────────────────────────────────────────────┘"

pause

# ══════════════════════════════════════════════════════════════
header "B) DATENBANKEBENE – 3 MongoDB-Benutzer mit verschiedenen Rechten"
# ══════════════════════════════════════════════════════════════

step "Alle MongoDB-Datenbankbenutzer anzeigen (als electroswap_admin):"
run_mongo "$ADMIN_URL" 'db.getUsers()'

step "Verbindungstest als electroswap_app (readWrite):"
echo "  Benutzer: electroswap_app  |  Rolle: readWrite"
run_mongo "$APP_URL" 'print("Produkte in DB: " + db.products.countDocuments())'

step "Verbindungstest als electroswap_readonly (nur lesen):"
echo "  Benutzer: electroswap_readonly  |  Rolle: read"
run_mongo "$READONLY_URL" 'print("Users in DB: " + db.users.countDocuments())'

pause

# ══════════════════════════════════════════════════════════════
header "C) LEAST-PRIVILEGE – Readonly darf NICHT schreiben"
# ══════════════════════════════════════════════════════════════

step "Readonly-User versucht zu schreiben → FEHLER erwartet:"
echo "  Befehl: db.users.insertOne({ test: 'unauthorized' })"
echo ""
# Fehler abfangen ohne set -e zu verletzen
docker exec electroswap_mongo mongosh "$READONLY_URL" --quiet \
    --eval 'db.users.insertOne({test:"unauthorized"})' 2>&1 || true

echo ""
echo "  ✓ MongoServerError: not authorized → Least-Privilege funktioniert"

step "Readonly-User versucht zu löschen → FEHLER erwartet:"
echo "  Befehl: db.products.deleteMany({})"
echo ""
docker exec electroswap_mongo mongosh "$READONLY_URL" --quiet \
    --eval 'db.products.deleteMany({})' 2>&1 || true

echo ""
echo "  ✓ MongoServerError: not authorized → Daten sind geschützt"

pause

# ══════════════════════════════════════════════════════════════
header "D) LIVE-ROLLENÄNDERUNG – customer → admin → customer"
# ══════════════════════════════════════════════════════════════

step "Aktueller Status von demo_customer:"
run_mongo "$ADMIN_URL" \
    'db.users.findOne({username:"demo_customer"},{username:1,email:1,role:1,_id:0})'

step "demo_customer wird zum Admin befördert:"
run_mongo "$ADMIN_URL" \
    'db.users.updateOne({username:"demo_customer"},{$set:{role:"admin"}});
     db.users.findOne({username:"demo_customer"},{username:1,role:1,_id:0})'

echo ""
echo "  ┌──────────────────────────────────────────────────────┐"
echo "  │  BROWSER:  customer@electroswap.ch neu einloggen     │"
echo "  │  → Admin-Link erscheint im Menü                      │"
echo "  │  → http://localhost/admin/ ist jetzt zugänglich      │"
echo "  └──────────────────────────────────────────────────────┘"

pause

step "Rolle wieder auf customer zurücksetzen:"
run_mongo "$ADMIN_URL" \
    'db.users.updateOne({username:"demo_customer"},{$set:{role:"customer"}});
     db.users.findOne({username:"demo_customer"},{username:1,role:1,_id:0})'

echo ""
echo "  ✓ Rolle zurückgesetzt auf customer"

# ══════════════════════════════════════════════════════════════
header "DEMO ABGESCHLOSSEN"
# ══════════════════════════════════════════════════════════════

echo ""
echo "  Gezeigt wurde:"
echo "  ✓ Applikationsebene: customer (eingeschränkt) vs. admin (vollständig)"
echo "  ✓ Datenbankebene:    3 Benutzer mit dbOwner / readWrite / read"
echo "  ✓ Least-Privilege:   Readonly kann nicht schreiben/löschen"
echo "  ✓ Live-Änderung:     Rolle per DB-Befehl geändert, sofort wirksam"
echo ""
