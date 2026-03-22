# restore.ps1 – ElectroSwap MongoDB Restore (Windows / PowerShell)
# Stellt die Datenbank aus einem zuvor erstellten Dump wieder her.
#
# Verwendung:
#   .\restore.ps1 -BackupName electroswap_20260321_120000
#
# Voraussetzung: Docker-Stack läuft (docker compose up)

param(
    [Parameter(Mandatory = $true)]
    [string]$BackupName
)

$dumpPath = ".\backup\dumps\$BackupName"

if (-not (Test-Path $dumpPath)) {
    Write-Host "Fehler: Backup-Ordner nicht gefunden: $dumpPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vorhandene Backups:"
    Get-ChildItem ".\backup\dumps" -Directory | ForEach-Object { Write-Host "  $($_.Name)" }
    exit 1
}

Write-Host "=== ElectroSwap Restore ===" -ForegroundColor Cyan
Write-Host "Backup  : $BackupName"
Write-Host ""
Write-Host "WARNUNG: Die bestehende 'electroswap'-Datenbank wird GELOSCHT und" -ForegroundColor Yellow
Write-Host "         durch den Backup-Stand ersetzt." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Fortfahren? (ja/nein)"

if ($confirm -ne "ja") {
    Write-Host "Abgebrochen."
    exit 0
}

Write-Host ""
Write-Host "Restore wird durchgeführt..."

# mongorestore im Container ausführen – liest aus /dump/$BackupName/electroswap
# Volume-Mount: ./backup/dumps <-> /dump (in docker-compose.yml definiert)
docker exec electroswap_mongo mongorestore `
    --username electroswap_admin `
    --password "AdminPass123!" `
    --authenticationDatabase electroswap `
    --db electroswap `
    --drop `
    "/dump/$BackupName/electroswap"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Restore abgeschlossen." -ForegroundColor Green
} else {
    Write-Host "Restore fehlgeschlagen (Exit-Code: $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}
