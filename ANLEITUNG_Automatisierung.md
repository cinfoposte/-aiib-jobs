# AIIB Feed - Automatische Aktualisierung einrichten

## Methode 1: Windows Aufgabenplanung (Empfohlen)

### Schritt-für-Schritt Anleitung:

1. **Aufgabenplanung öffnen:**
   - Drücken Sie `Windows-Taste + R`
   - Geben Sie ein: `taskschd.msc`
   - Drücken Sie Enter

2. **Neue Aufgabe erstellen:**
   - Klicken Sie rechts auf: **"Einfache Aufgabe erstellen..."**

3. **Aufgabe benennen:**
   - Name: `AIIB Feed Update`
   - Beschreibung: `Aktualisiert täglich die AIIB Jobausschreibungen`
   - Klicken Sie auf **"Weiter"**

4. **Trigger festlegen:**
   - Wählen Sie: **"Täglich"**
   - Klicken Sie auf **"Weiter"**

5. **Zeitpunkt festlegen:**
   - Startdatum: Heute
   - Uhrzeit: `09:00:00` (oder wann Sie möchten)
   - Wiederholen: Jeden 1 Tag
   - Klicken Sie auf **"Weiter"**

6. **Aktion auswählen:**
   - Wählen Sie: **"Programm starten"**
   - Klicken Sie auf **"Weiter"**

7. **Programm konfigurieren:**
   - **Programm/Skript:**
     ```
     C:\Users\carol\aiib-scraper\update_feed.bat
     ```
   - **Argumente:** (leer lassen)
   - **Starten in:**
     ```
     C:\Users\carol\aiib-scraper
     ```
   - Klicken Sie auf **"Weiter"**

8. **Fertigstellen:**
   - Setzen Sie Häkchen bei: **"Eigenschaftendialog... öffnen"**
   - Klicken Sie auf **"Fertig stellen"**

9. **Erweiterte Einstellungen (optional):**
   - Tab **"Allgemein"**:
     - ☑ Ausführen, auch wenn Benutzer nicht angemeldet ist
     - ☑ Mit höchsten Privilegien ausführen
   - Tab **"Einstellungen"**:
     - ☑ Aufgabe so schnell wie möglich nach einem verpassten Start ausführen
   - Klicken Sie auf **"OK"**

10. **Aufgabe testen:**
    - Rechtsklick auf die neue Aufgabe: **"Ausführen"**
    - Überprüfen Sie, ob `aiib_jobs.xml` aktualisiert wurde

---

## Methode 2: Manuelles Update (Schnell)

Doppelklicken Sie auf:
```
C:\Users\carol\aiib-scraper\update_feed.bat
```

Der Feed wird sofort aktualisiert!

---

## Methode 3: PowerShell Scheduler (Fortgeschritten)

Falls Sie mehr Kontrolle möchten, können Sie auch einen PowerShell Task Scheduler verwenden.

---

## Zeitplan-Empfehlungen:

- **Täglich um 9:00 Uhr** - Standard, für regelmäßige Updates
- **Mehrmals täglich** (z.B. 9:00, 14:00, 18:00) - Für häufigere Updates
- **Wöchentlich** - Falls Jobs sich selten ändern

---

## Wichtig:

⚠️ **Ihr Computer muss zur geplanten Zeit eingeschaltet sein**, damit die Aufgabe ausgeführt wird!

Alternative: Richten Sie "Ausführen, auch wenn Benutzer nicht angemeldet ist" ein (siehe Schritt 9).

---

## Upload ins Jobportal

Nach jedem Update finden Sie die aktualisierte Datei hier:
```
C:\Users\carol\aiib-scraper\aiib_jobs.xml
```

**Nächste Schritte:**
1. Laden Sie die Datei in Ihr Jobportal hoch
2. Wiederholen Sie dies nach jedem automatischen Update

**Tipp:** Falls Ihr Jobportal eine API hat, können wir das Upload auch automatisieren!

---

## Fehlerbehebung

**Problem:** Aufgabe läuft nicht
- Überprüfen Sie den Task-History in der Aufgabenplanung
- Testen Sie das Batch-Skript manuell
- Stellen Sie sicher, dass Python installiert ist

**Problem:** Chrome-Fehler
- Stellen Sie sicher, dass Chrome aktuell ist
- ChromeDriver wird automatisch heruntergeladen

---

Bei Fragen oder Problemen, führen Sie das Batch-Skript manuell aus, um Fehlermeldungen zu sehen.
