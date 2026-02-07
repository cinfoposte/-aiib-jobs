# AIIB Feed - Automatische Aufgabenplanung einrichten
# Dieses Skript erstellt automatisch eine Windows-Aufgabe

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AIIB Feed - Automatisches Update Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Pfade definieren
$scriptPath = "C:\Users\carol\aiib-scraper\update_feed.bat"
$workingDir = "C:\Users\carol\aiib-scraper"

# Prüfen ob Batch-Datei existiert
if (-not (Test-Path $scriptPath)) {
    Write-Host "FEHLER: update_feed.bat nicht gefunden!" -ForegroundColor Red
    Write-Host "Pfad: $scriptPath" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Batch-Skript gefunden: $scriptPath" -ForegroundColor Green
Write-Host ""

# Update-Zeit abfragen
Write-Host "Wann soll der Feed täglich aktualisiert werden?" -ForegroundColor Yellow
Write-Host "Beispiele: 09:00, 14:30, 08:00" -ForegroundColor Gray
Write-Host ""
$updateTime = Read-Host "Uhrzeit eingeben (Format: HH:MM)"

# Validierung der Zeitangabe
try {
    $time = [DateTime]::ParseExact($updateTime, "HH:mm", $null)
    Write-Host ""
    Write-Host "Update-Zeit gesetzt auf: $updateTime" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "FEHLER: Ungültige Zeitangabe. Verwende Standard: 09:00" -ForegroundColor Yellow
    $updateTime = "09:00"
    $time = [DateTime]::ParseExact($updateTime, "HH:mm", $null)
}

Write-Host ""
Write-Host "Erstelle Windows-Aufgabe..." -ForegroundColor Cyan

# Aufgabenname
$taskName = "AIIB_Feed_Update"

# Alte Aufgabe löschen falls vorhanden
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Lösche alte Aufgabe..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Neue Aufgabe erstellen
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

$trigger = New-ScheduledTaskTrigger -Daily -At $updateTime

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Highest

# Aufgabe registrieren
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Aktualisiert täglich die AIIB Job-Ausschreibungen und speichert sie als RSS-Feed" `
        -ErrorAction Stop

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Automatisches Update aktiviert!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Einstellungen:" -ForegroundColor Cyan
    Write-Host "  - Aufgabenname: $taskName" -ForegroundColor White
    Write-Host "  - Aktualisierung: Täglich um $updateTime" -ForegroundColor White
    Write-Host "  - Skript: $scriptPath" -ForegroundColor White
    Write-Host "  - Ausgabe: $workingDir\aiib_jobs.xml" -ForegroundColor White
    Write-Host ""
    Write-Host "Die Aufgabe läuft ab jetzt automatisch!" -ForegroundColor Green
    Write-Host ""

    # Frage ob Test gewünscht
    Write-Host "Möchten Sie die Aufgabe jetzt einmal testen? (J/N)" -ForegroundColor Yellow
    $test = Read-Host

    if ($test -eq "J" -or $test -eq "j" -or $test -eq "Y" -or $test -eq "y") {
        Write-Host ""
        Write-Host "Starte Test..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $taskName
        Write-Host "Test gestartet! Überprüfen Sie gleich die Datei aiib_jobs.xml" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "Sie können die Aufgabe in der Aufgabenplanung verwalten:" -ForegroundColor Cyan
    Write-Host "Windows-Taste + R -> taskschd.msc -> Aufgabe: $taskName" -ForegroundColor Gray

} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "FEHLER beim Erstellen der Aufgabe!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Fehlermeldung: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Mögliche Lösungen:" -ForegroundColor Yellow
    Write-Host "1. Führen Sie PowerShell als Administrator aus" -ForegroundColor White
    Write-Host "2. Prüfen Sie Ihre Berechtigungen" -ForegroundColor White
}

Write-Host ""
Write-Host "Drücken Sie eine Taste zum Beenden..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
