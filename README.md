# AIIB Job Scraper

Ein Python-Skript, das aktuelle Stellenangebote von der AIIB-Website extrahiert und als RSS-Feed im XML-Format speichert.

## Features

✓ Extrahiert alle aktuellen Jobausschreibungen von der AIIB-Website
✓ Verwendet Selenium mit Chrome für JavaScript-Rendering
✓ Extrahiert Jobtitel, Links und Bewerbungsfristen (Closing Dates)
✓ Speichert Daten im RSS 2.0 Format als `aiib_jobs.xml`
✓ Funktioniert mit dynamisch geladenen Inhalten

## Voraussetzungen

- Python 3.7 oder höher
- Google Chrome Browser (wird von Selenium verwendet)

## Installation

1. Navigiere zum Projektverzeichnis:
```bash
cd aiib-scraper
```

2. Installiere die erforderlichen Pakete:
```bash
py -m pip install -r requirements.txt
```

3. Installiere Selenium und webdriver-manager:
```bash
py -m pip install selenium webdriver-manager
```

## Verwendung

Führe das Skript aus:

```bash
py aiib_scraper.py
```

Das Skript wird:
1. Chrome im Headless-Modus starten
2. Die AIIB-Website laden und JavaScript ausführen
3. Auf das Laden der Job-Daten warten
4. Alle Jobs extrahieren (Current Opportunities + Future Opportunities)
5. Die Daten als `aiib_jobs.xml` speichern

## Ausgabe

Die RSS-Feed-Datei `aiib_jobs.xml` enthält:

- **Jobtitel** - Vollständiger Titel der Position
- **Link** - URL zur detaillierten Stellenbeschreibung
- **Closing Date** - Bewerbungsfrist
- **Posting Date** - Veröffentlichungsdatum (falls verfügbar)

### Beispiel RSS-Feed Struktur:

```xml
<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>AIIB Job Vacancies</title>
    <link>https://www.aiib.org/...</link>
    <description>Current job opportunities at AIIB</description>
    <item>
      <title>Senior Investment Solutions Specialist (PPP)</title>
      <link>https://www.aiib.org/.../job-details/...</link>
      <description>Position: ...
Closing Date: Feb 27, 2026</description>
      <closingDate>Feb 27, 2026</closingDate>
    </item>
  </channel>
</rss>
```

## Aktuelle Ergebnisse

Das Skript findet derzeit **50 Stellenausschreibungen**, einschließlich:
- Senior Investment Solutions Specialist (PPP)
- Senior Financial Sector Specialist
- Manager, Project & Corporate Finance
- Environment Specialist
- Digital Program Specialists
- Graduate Programs und Internships
- Und viele mehr...

## Technische Details

### Architektur

- **Selenium WebDriver**: Rendert JavaScript-Inhalte
- **BeautifulSoup**: Parsed HTML-Struktur
- **ChromeDriver**: Automatisch verwaltet durch webdriver-manager

### Parser-Strategien

1. **Primäre Strategie**: Parst div-basierte Tabellenstruktur (`<ul class="table-row">`)
2. **Fallback**: Traditionelles HTML-Tabellen-Parsing (`<table>` tags)

### Erkannte HTML-Struktur

Jobs werden in folgender Struktur geparst:
```html
<ul class="table-row">
  <div class="pCopy1">Jobtitel</div>
  <a class="viewLink" href="...">VIEW</a>
  <div class="pDate">Posting Date</div>
  <div class="cDate">Closing Date</div>
</ul>
```

## Debugging

Bei Problemen:
1. Überprüfe `debug_page.html` - enthält die gerenderte HTML-Seite
2. Stelle sicher, dass Chrome installiert ist
3. Prüfe die Internetverbindung

## Hinweise

- Das Skript benötigt eine Internetverbindung
- Chrome wird im Headless-Modus ausgeführt (unsichtbar)
- Die erste Ausführung lädt automatisch den passenden ChromeDriver herunter
- Timeout: 15 Sekunden für Seitenladen, 3 Sekunden zusätzlich für dynamische Inhalte

## Lizenz

Dieses Skript dient ausschließlich zu Informationszwecken. Bitte beachte die Nutzungsbedingungen der AIIB-Website.
