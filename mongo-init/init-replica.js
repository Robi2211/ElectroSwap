// ============================================================
// init-replica.js – MongoDB Replica Set Initialisierung
// Läuft einmalig nach dem Start aller 3 MongoDB-Nodes.
// ============================================================
// Ausgeführt von: mongo-init-replica Container (docker-compose)
// Verbindet als: root@admin
// ============================================================

// ── Prüfen ob Replica Set bereits konfiguriert ───────────────
try {
    var status = rs.status();
    if (status.ok === 1 && status.set === "rs0") {
        print("Replica Set 'rs0' bereits initialisiert – nichts zu tun.");
        quit(0);
    }
} catch (e) {
    // Erwartet: noch kein Replica Set konfiguriert
}

// ── Replica Set initialisieren mit 3 Nodes ───────────────────
print("Initialisiere Replica Set 'rs0'...");
print("  Node 0: mongo1:27017 (bevorzugter Primary, priority=2)");
print("  Node 1: mongo2:27017 (Secondary, priority=1)");
print("  Node 2: mongo3:27017 (Secondary, priority=1)");

var result = rs.initiate({
    _id: "rs0",
    members: [
        { _id: 0, host: "mongo1:27017", priority: 2 },
        { _id: 1, host: "mongo2:27017", priority: 1 },
        { _id: 2, host: "mongo3:27017", priority: 1 }
    ]
});

if (result.ok !== 1) {
    print("FEHLER bei rs.initiate(): " + JSON.stringify(result));
    quit(1);
}
print("rs.initiate() OK.");

// ── Warten bis PRIMARY gewählt wurde ─────────────────────────
print("Warte auf PRIMARY-Wahl (max. 60s)...");
var elapsed = 0;
var elected = false;
while (elapsed < 60000) {
    sleep(2000);
    elapsed += 2000;
    try {
        if (db.isMaster().ismaster) {
            elected = true;
            print("PRIMARY nach " + (elapsed / 1000) + "s gewählt.");
            break;
        }
        print("  Noch kein PRIMARY (" + (elapsed / 1000) + "s)...");
    } catch (e) {
        print("  Verbindung unterbrochen – reconnect...");
    }
}

if (!elected) {
    print("FEHLER: Kein PRIMARY nach 60s. Abbruch.");
    quit(1);
}

// ── Applikations-Benutzer erstellen ──────────────────────────
print("Erstelle Datenbankbenutzer auf electroswap...");
var db_es = db.getSiblingDB("electroswap");

// Admin (dbOwner – für Backup/Restore mit --drop)
try {
    db_es.createUser({
        user: "electroswap_admin",
        pwd: "AdminPass123!",
        roles: [{ role: "dbOwner", db: "electroswap" }]
    });
    print("  [OK] electroswap_admin (dbOwner)");
} catch (e) {
    print("  [--] electroswap_admin bereits vorhanden.");
}

// App-User (readWrite – Flask-Applikation)
try {
    db_es.createUser({
        user: "electroswap_app",
        pwd: "AppPass456!",
        roles: [{ role: "readWrite", db: "electroswap" }]
    });
    print("  [OK] electroswap_app (readWrite)");
} catch (e) {
    print("  [--] electroswap_app bereits vorhanden.");
}

// Readonly-User (read – Backups, Reporting)
try {
    db_es.createUser({
        user: "electroswap_readonly",
        pwd: "ReadPass789!",
        roles: [{ role: "read", db: "electroswap" }]
    });
    print("  [OK] electroswap_readonly (read)");
} catch (e) {
    print("  [--] electroswap_readonly bereits vorhanden.");
}

// ── Abschlussstatus ───────────────────────────────────────────
print("");
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
print("  Replica Set 'rs0' initialisiert – Memberstatus:");
rs.status().members.forEach(function(m) {
    print("  " + m.name + " → " + m.stateStr);
});
print("  Benutzer erstellt: admin / app / readonly");
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
