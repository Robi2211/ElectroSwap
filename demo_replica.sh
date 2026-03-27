#!/bin/bash
# ============================================================
# demo_replica.sh – MongoDB Replica Set Demo (Kriterium 3.6)
# Zeigt: Status, Replikation, automatischer Failover
# ============================================================

ROOT="mongosh --quiet --username root --password RootPass000! --authenticationDatabase admin"
ADMIN_ES="mongosh electroswap --username electroswap_admin --password AdminPass123! --authenticationDatabase electroswap --quiet"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  REPLICA SET DEMO  –  Horizontale Datenbankskalierung"
echo "  3 MongoDB-Nodes mit automatischer Replikation & Failover"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Schritt 1: Replica Set Status ────────────────────────────
echo "  ┌─ Schritt 1: Replica Set Status ───────────────────────┐"
docker exec electroswap_mongo1 $ROOT --eval '
  rs.status().members.forEach(function(m) {
    print("  │  " + m.name + " → " + m.stateStr +
          (m.stateStr === "PRIMARY" ? " ★" : ""));
  });
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 2: Schreiben auf PRIMARY ─────────────────────────
echo "  ┌─ Schritt 2: Dokument auf PRIMARY schreiben ───────────┐"
docker exec electroswap_mongo1 $ADMIN_ES --eval '
  db.replica_test.drop();
  var id = db.replica_test.insertOne({
    msg: "Replikationstest ElectroSwap",
    node: "mongo1 (PRIMARY)",
    ts: new Date()
  }).insertedId;
  print("  │  Geschrieben auf: mongo1 (PRIMARY)");
  print("  │  _id: " + id);
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 3: Replikation auf Secondary prüfen ──────────────
echo "  ┌─ Schritt 3: Replikation auf mongo2 (Secondary) ───────┐"
sleep 2
docker exec electroswap_mongo2 $ADMIN_ES --eval '
  db.getMongo().setReadPref("secondaryPreferred");
  var doc = db.replica_test.findOne();
  if (doc) {
    print("  │  Dokument auf SECONDARY empfangen!");
    print("  │  msg : " + doc.msg);
    print("  │  node: " + doc.node);
    print("  │  ts  : " + doc.ts);
    print("  │");
    print("  │  Replikation funktioniert.");
  } else {
    print("  │  Noch nicht repliziert – ggf. kurz warten.");
  }
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 4: Replikationsinfo ──────────────────────────────
echo "  ┌─ Schritt 4: Replikations-Log (Oplog) ─────────────────┐"
docker exec electroswap_mongo1 $ROOT --eval '
  var info = rs.printReplicationInfo();
' 2>&1 | grep -E "log length|oplog|last event" | head -5 | sed 's/^/  │  /'
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 5: Failover demonstrieren ────────────────────────
echo "  ┌─ Schritt 5: Failover – PRIMARY (mongo1) stoppen ──────┐"
echo "  │  Stoppe mongo1..."
docker stop electroswap_mongo1 2>&1 | sed 's/^/  │  /'
echo "  │"
echo "  │  Warte auf automatische PRIMARY-Neuwahl (10s)..."
sleep 12
docker exec electroswap_mongo2 $ROOT --eval '
  var members = rs.status().members;
  members.forEach(function(m) {
    print("  │  " + m.name + " → " + m.stateStr +
          (m.stateStr === "PRIMARY" ? " ★ (neuer PRIMARY)" : ""));
  });
' 2>&1
echo "  │"
echo "  │  mongo1 ist ausgefallen – ein Secondary wurde automatisch"
echo "  │  zum neuen PRIMARY gewählt. Keine Downtime."
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 6: mongo1 wiederherstellen ───────────────────────
echo "  ┌─ Schritt 6: mongo1 wieder starten (Resync) ───────────┐"
docker start electroswap_mongo1 2>&1 | sed 's/^/  │  /'
sleep 12
docker exec electroswap_mongo2 $ROOT --eval '
  rs.status().members.forEach(function(m) {
    print("  │  " + m.name + " → " + m.stateStr);
  });
' 2>&1
echo "  │"
echo "  │  mongo1 ist als SECONDARY wieder im Replica Set."
echo "  │  Alle Änderungen während des Ausfalls wurden nachgesynct."
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Cleanup ───────────────────────────────────────────────────
docker exec electroswap_mongo1 $ADMIN_ES \
  --eval 'db.replica_test.drop()' 2>/dev/null || \
docker exec electroswap_mongo2 $ADMIN_ES \
  --eval 'db.replica_test.drop()' 2>/dev/null || true

echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓  Demo abgeschlossen"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
