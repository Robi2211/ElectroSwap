#!/bin/bash
# ============================================================
# demo_restore.sh  –  Restore mit Admin-Benutzer
# Admin-User wird benötigt (--drop erfordert Schreibrecht)
# ============================================================
#
# Verwendung:
#   bash demo_restore.sh [archivdatei.gz]
# Kein Argument → neuestes Backup wird automatisch gewählt

ARCHIVE="$1"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  RESTORE DEMO – mit Admin-Authentifizierung"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Neuestes Backup wählen wenn kein Argument
if [ -z "$ARCHIVE" ]; then
    ARCHIVE=$(ls -t ./backup/dumps/electroswap_*.gz 2>/dev/null | head -1)
    if [ -z "$ARCHIVE" ]; then
        echo "  FEHLER: Kein Backup gefunden in ./backup/dumps/"
        echo "  Zuerst ausführen: bash demo_backup.sh"
        exit 1
    fi
    echo "  Kein Archiv angegeben → verwende neuestes Backup:"
fi

if [ ! -f "$ARCHIVE" ]; then
    echo "  FEHLER: Datei nicht gefunden: $ARCHIVE"
    exit 1
fi

echo "  Benutzer : electroswap_admin  (Rolle: dbOwner – für --drop nötig)"
echo "  Passwort : AdminPass123!"
echo "  Archiv   : $ARCHIVE"
echo ""

# ── Zustand VOR dem Restore ──────────────────────────────────
echo "  ┌─ Zustand VOR dem Restore ─────────────────────────────┐"
docker exec electroswap_mongo1 mongosh electroswap \
    --username electroswap_admin \
    --password "AdminPass123!" \
    --authenticationDatabase electroswap \
    --quiet \
    --eval 'print("  │  products: " + db.products.countDocuments() +
                  " | users: "   + db.users.countDocuments() +
                  " | orders: "  + db.orders.countDocuments() +
                  " | reviews: " + db.reviews.countDocuments())' 2>&1
echo "  └───────────────────────────────────────────────────────┘"

echo ""
echo "  Starte mongorestore (--drop: bestehende Collections werden überschrieben)..."
echo ""

gunzip -c "$ARCHIVE" | docker exec -i electroswap_mongo1 mongorestore \
    --username electroswap_admin \
    --password "AdminPass123!" \
    --authenticationDatabase electroswap \
    --db electroswap \
    --drop \
    --archive 2>&1 | grep -E "done|restoring|error|finished" | tail -10

echo ""

# ── Zustand NACH dem Restore ─────────────────────────────────
echo "  ┌─ Zustand NACH dem Restore ────────────────────────────┐"
docker exec electroswap_mongo1 mongosh electroswap \
    --username electroswap_admin \
    --password "AdminPass123!" \
    --authenticationDatabase electroswap \
    --quiet \
    --eval 'print("  │  products: " + db.products.countDocuments() +
                  " | users: "   + db.users.countDocuments() +
                  " | orders: "  + db.orders.countDocuments() +
                  " | reviews: " + db.reviews.countDocuments())' 2>&1
echo "  └───────────────────────────────────────────────────────┘"

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ Restore abgeschlossen – Daten wiederhergestellt."
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
