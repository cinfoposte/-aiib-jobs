#!/usr/bin/env python3
"""
AIIB Job Scraper
Scrapes job listings from AIIB website and generates an RSS feed
Format: cinfoPoste-compatible (based on World Bank reference implementation)
"""

import time
import os
import shutil
import hashlib
import html as html_module
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone
from email.utils import format_datetime

import requests
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    USE_SELENIUM = True
except ImportError:
    USE_SELENIUM = False
    print("Warning: Selenium not installed. JavaScript rendering not available.")


# ── Constants ────────────────────────────────────────────────────────────────

AIIB_URL = "https://www.aiib.org/en/opportunities/career/job-vacancies/staff/index.html"
FEED_FILE = "aiib_jobs.xml"
FEED_SELF_URL = "https://cinfoposte.github.io/aiib-jobs/aiib_jobs.xml"


# ── Helpers ───────────────────────────────────────────────────────────────────

def generate_numeric_id(url: str) -> str:
    """Generate a stable 16-digit numeric GUID from a URL (MD5-based)."""
    hex_dig = hashlib.md5(url.encode()).hexdigest()
    return str(int(hex_dig[:16], 16) % 10_000_000_000_000_000)


def rfc2822_now() -> str:
    """Return current UTC time in RFC 2822 format (includes weekday)."""
    return format_datetime(datetime.now(timezone.utc))


def get_existing_links(feed_file: str = FEED_FILE) -> set:
    """Read job links already present in the existing feed to skip duplicates."""
    existing = set()
    if not os.path.exists(feed_file):
        print("No existing feed found – all jobs treated as new.")
        return existing
    try:
        tree = ET.parse(feed_file)
        for link_elem in tree.getroot().findall(".//item/link"):
            if link_elem.text:
                existing.add(link_elem.text.strip())
        print(f"Found {len(existing)} existing job(s) in previous feed.")
    except Exception as e:
        print(f"Could not read existing feed: {e} – treating all jobs as new.")
    return existing


# ── Selenium driver ───────────────────────────────────────────────────────────

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    chromedriver_path = shutil.which("chromedriver")
    service = Service(chromedriver_path) if chromedriver_path else Service("chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)


# ── Fetch page ────────────────────────────────────────────────────────────────

def fetch_page() -> str | None:
    if USE_SELENIUM:
        print("Using Selenium to render JavaScript …")
        driver = None
        try:
            driver = setup_driver()
            driver.get(AIIB_URL)
            print("Waiting 20 s for JavaScript rendering …")
            time.sleep(20)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            return driver.page_source
        except Exception as e:
            print(f"Selenium error: {e} – falling back to requests.")
        finally:
            if driver:
                driver.quit()

    print("Using requests (JavaScript will NOT be rendered) …")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get(AIIB_URL, headers=headers, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"requests error: {e}")
        return None


# ── Parse jobs ────────────────────────────────────────────────────────────────

def parse_jobs(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    seen = set()

    # Strategy 1 – div-based table (current AIIB structure)
    job_rows = soup.find_all("ul", class_="table-row")
    print(f"Strategy 1: {len(job_rows)} row(s) found.")

    for row in job_rows:
        try:
            title_div = row.find("div", class_="pCopy1")
            if not title_div:
                continue
            title = title_div.get_text(strip=True)
            if not title or len(title) < 5:
                continue

            link_tag = row.find("a", class_="viewLink")
            href = link_tag.get("href", "") if link_tag else ""
            if href and not href.startswith("http"):
                href = f"https://www.aiib.org{href}"
            if not href:
                href = AIIB_URL

            if href in seen:
                continue
            seen.add(href)

            closing = ""
            c = row.find("div", class_="cDate")
            if c:
                closing = c.get_text(strip=True)

            location = "Beijing, China"  # AIIB HQ default

            jobs.append({
                "title": title,
                "link": href,
                "location": location,
                "closing_date": closing,
            })
            print(f"  [OK] {title}")

        except Exception as e:
            print(f"  [ERROR] {e}")
            continue

    # Strategy 2 – traditional HTML table fallback
    if not jobs:
        print("Strategy 2: trying HTML tables …")
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True).upper() for th in table.find_all("th")]
            if "POSITION" not in headers:
                continue
            pos_idx = headers.index("POSITION")
            rows = (table.find("tbody") or table).find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) <= pos_idx:
                    continue
                a = cells[pos_idx].find("a")
                if not a:
                    continue
                title = a.get_text(strip=True)
                href = a.get("href", "")
                if href and not href.startswith("http"):
                    href = f"https://www.aiib.org{href}"
                if not href:
                    href = AIIB_URL
                if href in seen:
                    continue
                seen.add(href)
                jobs.append({
                    "title": title,
                    "link": href,
                    "location": "Beijing, China",
                    "closing_date": "",
                })
                print(f"  [OK] {title}")

    print(f"\nTotal jobs parsed: {len(jobs)}")
    return jobs


# ── Build RSS feed ────────────────────────────────────────────────────────────

def generate_rss_feed(jobs: list[dict], output_file: str = FEED_FILE):
    """Write an RSS 2.0 feed in cinfoPoste-compatible format."""

    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')

    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    rss.set("xml:base", "https://www.aiib.org/")

    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "AIIB Job Vacancies"
    ET.SubElement(channel, "link").text = AIIB_URL
    ET.SubElement(channel, "description").text = (
        "Current job opportunities at Asian Infrastructure Investment Bank (AIIB)"
    )
    ET.SubElement(channel, "language").text = "en"

    atom_link = ET.SubElement(channel, "atom:link")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")
    atom_link.set("href", FEED_SELF_URL)

    ET.SubElement(channel, "pubDate").text = rfc2822_now()

    now_str = rfc2822_now()

    for job in jobs:
        item = ET.SubElement(channel, "item")

        ET.SubElement(item, "title").text = job["title"]
        ET.SubElement(item, "link").text = job["link"]

        # Description – plain text; CDATA applied later via minidom
        desc = f"AIIB has a vacancy for the position of {job['title']}. Location: {job['location']}."
        if job.get("closing_date"):
            desc += f" Closing date: {job['closing_date']}."
        ET.SubElement(item, "description").text = desc

        # GUID – stable numeric ID derived from URL
        guid = ET.SubElement(item, "guid")
        guid.set("isPermaLink", "false")
        guid.text = generate_numeric_id(job["link"])

        ET.SubElement(item, "pubDate").text = now_str

        source = ET.SubElement(item, "source")
        source.set("url", AIIB_URL)
        source.text = "AIIB Job Vacancies"

    # Pretty-print via minidom and wrap descriptions in CDATA
    xml_string = ET.tostring(rss, encoding="unicode")
    dom = minidom.parseString(xml_string)

    for item_node in dom.getElementsByTagName("item"):
        for desc_node in item_node.getElementsByTagName("description"):
            raw = desc_node.firstChild.nodeValue if desc_node.firstChild else ""
            safe = html_module.escape(raw, quote=False)
            while desc_node.firstChild:
                desc_node.removeChild(desc_node.firstChild)
            desc_node.appendChild(dom.createCDATASection(safe))

    pretty = "\n".join(
        line for line in dom.toprettyxml(indent="  ").split("\n") if line.strip()
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty)

    print(f"\n[SUCCESS] Feed written: {output_file}  ({len(jobs)} job(s))")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("AIIB Job Scraper  (cinfoPoste-compatible)")
    print("=" * 60)

    existing_links = get_existing_links()

    html = fetch_page()
    if not html:
        print("[ERROR] Could not fetch page.")
        return

    all_jobs = parse_jobs(html)
    new_jobs = [j for j in all_jobs if j["link"] not in existing_links]

    print("\n" + "=" * 60)
    print(f"Total jobs found    : {len(all_jobs)}")
    print(f"New jobs            : {len(new_jobs)}")
    print(f"Skipped (duplicate) : {len(all_jobs) - len(new_jobs)}")
    print("=" * 60)

    if new_jobs:
        generate_rss_feed(new_jobs)
        print("\nNew jobs added:")
        for i, j in enumerate(new_jobs, 1):
            print(f"  {i}. {j['title']}")
    else:
        print("\n[INFO] No new jobs – feed not updated.")
        if not os.path.exists(FEED_FILE):
            print("[INFO] Creating empty feed.")
            generate_rss_feed([])

    print("=" * 60)


if __name__ == "__main__":
    main()
