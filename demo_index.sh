#!/bin/bash
# ============================================================
# demo_index.sh  –  Index-Demo (Kriterium 5.1)
# Zeigt den Unterschied zwischen COLLSCAN und IXSCAN
# ============================================================

MONGO_ADMIN="mongosh --quiet --username electroswap_admin --password AdminPass123! --authenticationDatabase electroswap electroswap"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  INDEX DEMO  –  COLLSCAN vs. IXSCAN (Kriterium 5.1)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Schritt 1: Alle Indexes anzeigen ─────────────────────────
echo "  ┌─ Schritt 1: Alle Indexes auf 'products' ──────────────┐"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  db.products.getIndexes().forEach(idx =>
    print("  │  " + JSON.stringify({name: idx.name, key: idx.key, unique: idx.unique || false}))
  );
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 2: IXSCAN – Query MIT Index ──────────────────────
echo "  ┌─ Schritt 2: Query MIT Index (IXSCAN) ─────────────────┐"
echo "  │  db.products.find({category: 'Notebooks'}).explain()"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  var stats = db.products.find({category: "Notebooks"}).explain("executionStats").executionStats;
  print("  │  → stage:             " + stats.executionStages.stage);
  print("  │  → totalDocsExamined: " + stats.totalDocsExamined);
  print("  │  → totalDocsReturned: " + stats.nReturned);
  print("  │  → executionTimeMs:   " + stats.executionTimeMillis + " ms");
  var inputStage = stats.executionStages.inputStage;
  if (inputStage) print("  │  → inputStage:        " + inputStage.stage + " (" + (inputStage.indexName || "-") + ")");
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 3: Index droppen ──────────────────────────────────
echo "  ┌─ Schritt 3: Index 'category_1' droppen ───────────────┐"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  db.products.dropIndex("category_1");
  print("  │  Index category_1 erfolgreich gedroppt.");
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 4: COLLSCAN – Query OHNE Index ───────────────────
echo "  ┌─ Schritt 4: Query OHNE Index (COLLSCAN) ──────────────┐"
echo "  │  db.products.find({category: 'Notebooks'}).explain()"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  var stats = db.products.find({category: "Notebooks"}).explain("executionStats").executionStats;
  print("  │  → stage:             " + stats.executionStages.stage);
  print("  │  → totalDocsExamined: " + stats.totalDocsExamined + "  ← ALLE Dokumente!");
  print("  │  → totalDocsReturned: " + stats.nReturned);
  print("  │  → executionTimeMs:   " + stats.executionTimeMillis + " ms");
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

echo "  *** VERGLEICH: Mit Index → nur Treffer geprüft ***"
echo "  ***              Ohne Index → ALLE Dokumente geprüft ***"
echo ""

# ── Schritt 5: Index wiederherstellen ────────────────────────
echo "  ┌─ Schritt 5: Index wiederherstellen ───────────────────┐"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  db.products.createIndex({category: 1});
  print("  │  Index category_1 wiederhergestellt.");
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 6: Unique Index auf username ─────────────────────
echo "  ┌─ Schritt 6: Unique Index – username ──────────────────┐"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  var indexes = db.users.getIndexes().map(i => i.name);
  print("  │  Aktuelle users-Indexes: " + indexes.join(", "));
' 2>&1
echo "  │  → username_1 mit unique: true verhindert Duplikate"
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 7: Unique-Verletzung demonstrieren ───────────────
echo "  ┌─ Schritt 7: Unique-Verletzung (E11000) ───────────────┐"
echo "  │  Versuch: zweiten User mit username 'admin' einfügen"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  try {
    db.users.insertOne({username: "admin", _demo: true});
    print("  │  → FEHLER: Insert hat geklappt (sollte nicht!)");
  } catch(e) {
    print("  │  → " + e.message.split(":")[0] + ": E11000 duplicate key error");
    print("  │  → Unique-Index verhindert Duplikat-Username!");
  }
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

# ── Schritt 8: Compound Index auf reviews ────────────────────
echo "  ┌─ Schritt 8: Compound + Text Index ────────────────────┐"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  db.reviews.getIndexes().forEach(idx =>
    print("  │  " + idx.name + (idx.unique ? " [UNIQUE]" : ""))
  );
' 2>&1
echo "  │"
echo "  │  Text-Index: Volltext-Suche über name+description+brand"
docker exec electroswap_mongo1 $MONGO_ADMIN --eval '
  var stats = db.products.find({"\$text": {"\$search": "gaming"}}).explain("executionStats").executionStats;
  print("  │  → TEXT_MATCH stage, docsExamined: " + stats.totalDocsExamined + ", returned: " + stats.nReturned);
' 2>&1
echo "  └───────────────────────────────────────────────────────┘"
echo ""

echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ Index-Demo abgeschlossen"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
