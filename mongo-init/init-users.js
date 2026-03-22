// MongoDB initialisation script – runs once when the container is first created.
// Creates the electroswap database together with dedicated DB users.

// ── 1. Admin-level DB user ────────────────────────────────────────────────────
db.getSiblingDB("electroswap").createUser({
  user: "electroswap_admin",
  pwd: "AdminPass123!",
  roles: [
    { role: "dbOwner", db: "electroswap" }
  ]
});

// ── 2. Application user (read + write, no schema changes) ────────────────────
db.getSiblingDB("electroswap").createUser({
  user: "electroswap_app",
  pwd: "AppPass456!",
  roles: [
    { role: "readWrite", db: "electroswap" }
  ]
});

// ── 3. Read-only user (reporting / backups) ───────────────────────────────────
db.getSiblingDB("electroswap").createUser({
  user: "electroswap_readonly",
  pwd: "ReadPass789!",
  roles: [
    { role: "read", db: "electroswap" }
  ]
});

print("MongoDB users created successfully.");
