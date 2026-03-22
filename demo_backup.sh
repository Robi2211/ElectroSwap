#!/bin/bash
# ============================================================
# demo_backup.sh  –  Backup mit korrektem Readonly-Benutzer
# Least-Privilege: Backup braucht nur Lesezugriff (read-Rolle)
# ============================================================

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE="./backup/dumps/electroswap_${TIMESTAMP}.gz"

mkdir -p ./backup/dumps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  BACKUP DEMO – Korrekte Authentifizierung (readonly-User)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Benutzer : electroswap_readonly  (Rolle: read – Least Privilege)"
echo "  Passwort : ReadPass789!"
echo "  Datenbank: electroswap"
echo "  Zieldatei: $ARCHIVE"
echo ""

# Aktuellen Datenbankstand anzeigen
echo "  Zustand VOR dem Backup:"
docker exec electroswap_mongo mongosh electroswap \
    --username electroswap_admin \
    --password "AdminPass123!" \
    --authenticationDatabase electroswap \
    --quiet \
    --eval 'print("  products: " + db.products.countDocuments() +
                  " | users: "   + db.users.countDocuments() +
                  " | orders: "  + db.orders.countDocuments())' 2>&1

echo ""
echo "  Starte mongodump..."
echo ""

docker exec electroswap_mongo mongodump \
    --username electroswap_readonly \
    --password "ReadPass789!" \
    --authenticationDatabase electroswap \
    --db electroswap \
    --archive | gzip > "$ARCHIVE"

echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ Backup erfolgreich erstellt!"
echo "    Datei  : $ARCHIVE"
echo "    Grösse : $(du -sh "$ARCHIVE" 2>/dev/null | cut -f1)"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Alle Backups in backup/dumps/:"
ls -lh ./backup/dumps/*.gz 2>/dev/null || echo "  (keine)"
echo ""

# Alte Backups bereinigen (>7 Tage)
find ./backup/dumps -name "electroswap_*.gz" -mtime +7 -delete 2>/dev/null && \
    echo "  Alte Backups (>7 Tage) automatisch bereinigt." || true
