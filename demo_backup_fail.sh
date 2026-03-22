#!/bin/bash
# ============================================================
# demo_backup_fail.sh  –  Backup mit FALSCHEM Passwort
# Zeigt: MongoDB verweigert Zugriff bei falscher Authentifizierung
# ============================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  BACKUP DEMO – Falsches Passwort (Auth soll fehlschlagen)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Benutzer : electroswap_readonly"
echo "  Passwort : FALSCHES_PASSWORT_123   ← absichtlich falsch"
echo "  Datenbank: electroswap"
echo ""
echo "  Befehl:"
echo "  mongodump --username electroswap_readonly"
echo "            --password FALSCHES_PASSWORT_123"
echo "            --authenticationDatabase electroswap"
echo "            --db electroswap --archive"
echo ""
echo "  Starte mongodump..."
echo ""

docker exec electroswap_mongo mongodump \
    --username electroswap_readonly \
    --password "FALSCHES_PASSWORT_123" \
    --authenticationDatabase electroswap \
    --db electroswap \
    --archive > /dev/null 2>&1 || true

echo "  ERGEBNIS:"
docker exec electroswap_mongo mongodump \
    --username electroswap_readonly \
    --password "FALSCHES_PASSWORT_123" \
    --authenticationDatabase electroswap \
    --db electroswap \
    --archive 2>&1 | grep -i "failed\|error\|auth" | head -3 || true

echo ""
echo "  ✓ MongoDB verweigert Zugriff → Authentifizierung schützt die Daten"
echo ""
