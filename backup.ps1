# backup.ps1 – ElectroSwap MongoDB Backup (Windows / PowerShell)
# Erstellt einen Dump mit Zeitstempel über das gemountete Volume.
#
# Verwendung:
#   .\backup.ps1
#
# Voraussetzung: Docker-Stack läuft (docker compose up)

$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "electroswap_$timestamp"

# backup/dumps/ erstellen falls nicht vorhanden
New-Item -ItemType Directory -Force -Path ".\backup\dumps" | Out-Null

Write-Host "=== ElectroSwap Backup ===" -ForegroundColor Cyan
Write-Host "Zeitstempel : $timestamp"
Write-Host "Zielordner  : .\backup\dumps\$backupName"
Write-Host ""

# mongodump im Container ausführen – schreibt in /dump/$backupName
# Volume-Mount: ./backup/dumps <-> /dump (in docker-compose.yml definiert)
docker exec electroswap_mongo mongodump `
    --username electroswap_readonly `
    --password "ReadPass789!" `
    --authenticationDatabase electroswap `
    --db electroswap `
    --out "/dump/$backupName"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Backup erfolgreich erstellt: .\backup\dumps\$backupName" -ForegroundColor Green
} else {
    Write-Host "Backup fehlgeschlagen (Exit-Code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}
