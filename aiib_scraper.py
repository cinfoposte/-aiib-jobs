#!/usr/bin/env python3
"""
AIIB Job Scraper - Extracts current job vacancies from AIIB website and saves as RSS feed
"""

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    USE_SELENIUM = True
except ImportError:
    USE_SELENIUM = False
    print("Warning: Selenium not installed. JavaScript rendering not available.")
    print("Install with: py -m pip install selenium webdriver-manager")

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import time


def fetch_jobs():
    """Fetch job listings from AIIB website"""
    url = "https://www.aiib.org/en/opportunities/career/job-vacancies/staff/index.html"

    if USE_SELENIUM:
        print("Using Selenium with Chrome to render JavaScript...")
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            # Initialize driver
            print("Initializing Chrome driver...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Load page
            print(f"Loading page: {url}")
            driver.get(url)

            # Wait for the job table to load
            print("Waiting for content to load...")
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "table-body"))
                )
                time.sleep(3)  # Additional wait for dynamic content
            except:
                print("Timeout waiting for table-body, continuing anyway...")

            # Get the page source after JavaScript execution
            html_content = driver.page_source
            return html_content

        except Exception as e:
            print(f"Error with Selenium: {e}")
            print("Falling back to regular requests...")
        finally:
            if driver:
                driver.quit()

    # Fallback to regular requests
    print("Using regular requests (JavaScript will NOT be rendered)...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None


def parse_jobs(html_content):
    """Parse HTML content and extract job information"""
    soup = BeautifulSoup(html_content, 'html.parser')
    jobs = []
    seen_links = set()  # Track unique jobs by link

    # Debug: Save HTML to file for inspection
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Saved rendered HTML to debug_page.html for inspection")

    # Strategy 1: Parse the div-based table structure (used by AIIB)
    # Job rows are in <ul class="table-row ...">
    job_rows = soup.find_all('ul', class_='table-row')
    print(f"Found {len(job_rows)} job row(s) in div-based structure")

    for row in job_rows:
        try:
            # Extract job title from pCopy1
            title_div = row.find('div', class_='pCopy1')
            if not title_div:
                continue

            job_title = title_div.get_text(strip=True)

            # Extract link
            link_tag = row.find('a', class_='viewLink')
            job_link = ""
            if link_tag and link_tag.get('href'):
                job_link = link_tag.get('href', '')
                if job_link and not job_link.startswith('http'):
                    job_link = f"https://www.aiib.org{job_link}"

            # Skip duplicates based on link
            if job_link and job_link in seen_links:
                continue
            if job_link:
                seen_links.add(job_link)

            # Extract closing date from cDate
            closing_date_div = row.find('div', class_='cDate')
            closing_date = closing_date_div.get_text(strip=True) if closing_date_div else "Not specified"

            # Extract posting date (optional)
            posting_date_div = row.find('div', class_='pDate')
            posting_date = posting_date_div.get_text(strip=True) if posting_date_div else ""

            if job_title:
                jobs.append({
                    'title': job_title,
                    'link': job_link,
                    'closing_date': closing_date,
                    'posting_date': posting_date,
                    'ref_number': ""
                })
                print(f"  -> Found: {job_title} (Closing: {closing_date})")

        except Exception as e:
            print(f"  Error parsing job row: {e}")
            continue

    # Strategy 2: Fallback to traditional HTML table parsing
    if not jobs:
        print("\nTrying traditional HTML table parsing...")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} HTML table(s)")

        for idx, table in enumerate(tables):
            headers = table.find_all('th')
            header_texts = [th.get_text(strip=True).upper() for th in headers]

            if 'POSITION' in header_texts and 'CLOSING DATE' in header_texts:
                print(f"  -> Table {idx + 1} matches! Parsing rows...")
                try:
                    position_idx = header_texts.index('POSITION')
                    closing_date_idx = header_texts.index('CLOSING DATE')
                    ref_number_idx = header_texts.index('REF. NUMBER') if 'REF. NUMBER' in header_texts else None
                except ValueError:
                    continue

                rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) <= max(position_idx, closing_date_idx):
                        continue

                    position_cell = cells[position_idx]
                    link_tag = position_cell.find('a')

                    if link_tag:
                        job_title = link_tag.get_text(strip=True)
                        job_link = link_tag.get('href', '')
                        if job_link and not job_link.startswith('http'):
                            job_link = f"https://www.aiib.org{job_link}"
                    else:
                        job_title = position_cell.get_text(strip=True)
                        job_link = ""

                    closing_date = cells[closing_date_idx].get_text(strip=True)

                    ref_number = ""
                    if ref_number_idx is not None and len(cells) > ref_number_idx:
                        ref_number = cells[ref_number_idx].get_text(strip=True)

                    if job_title and closing_date:
                        jobs.append({
                            'title': job_title,
                            'link': job_link,
                            'closing_date': closing_date,
                            'posting_date': '',
                            'ref_number': ref_number
                        })
                        print(f"     -> Found job: {job_title}")

    if not jobs:
        print("\nNo jobs found with any parsing strategy.")

    return jobs


def create_rss_feed(jobs):
    """Create RSS feed XML from job data"""

    # Create RSS root element
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')

    # Create channel
    channel = ET.SubElement(rss, 'channel')

    # Add channel metadata
    title = ET.SubElement(channel, 'title')
    title.text = 'AIIB Job Vacancies'

    link = ET.SubElement(channel, 'link')
    link.text = 'https://www.aiib.org/en/opportunities/career/job-vacancies/staff/index.html'

    # Add atom:link with rel="self"
    atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
    atom_link.set('href', 'https://www.aiib.org/en/opportunities/career/job-vacancies/staff/index.html')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    description = ET.SubElement(channel, 'description')
    description.text = 'Current job opportunities at Asian Infrastructure Investment Bank (AIIB)'

    language = ET.SubElement(channel, 'language')
    language.text = 'en'

    last_build_date = ET.SubElement(channel, 'lastBuildDate')
    last_build_date.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

    # Add job items
    for job in jobs:
        item = ET.SubElement(channel, 'item')

        item_title = ET.SubElement(item, 'title')
        item_title.text = job['title']

        item_link = ET.SubElement(item, 'link')
        item_link.text = job['link'] if job['link'] else link.text

        item_description = ET.SubElement(item, 'description')
        desc_text = f"Position: {job['title']}"
        if job['ref_number']:
            desc_text += f"\nReference Number: {job['ref_number']}"
        desc_text += f"\nClosing Date: {job['closing_date']}"
        if job.get('posting_date'):
            desc_text += f"\nPosting Date: {job['posting_date']}"
        item_description.text = desc_text

        # Add closing date as pubDate (parse if possible)
        pub_date = ET.SubElement(item, 'pubDate')
        pub_date.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

        # Add GUID
        guid = ET.SubElement(item, 'guid')
        guid.set('isPermaLink', 'true')
        guid.text = job['link'] if job['link'] else f"{link.text}#{job['title']}"

    return rss


def prettify_xml(elem):
    """Return a pretty-printed XML string"""
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


def save_rss_feed(rss_element, filename='aiib_jobs.xml'):
    """Save RSS feed to XML file"""
    xml_string = prettify_xml(rss_element)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_string)

    print(f"RSS feed saved to {filename}")


def main():
    print("Fetching AIIB job vacancies...")
    html_content = fetch_jobs()

    if not html_content:
        print("Failed to fetch job listings")
        return

    print("Parsing job listings...")
    jobs = parse_jobs(html_content)

    if not jobs:
        print("No current job openings found")
        print("Creating empty RSS feed...")
    else:
        print(f"Found {len(jobs)} job(s)")
        for job in jobs:
            print(f"  - {job['title']} (Closing: {job['closing_date']})")

    print("\nGenerating RSS feed...")
    rss_feed = create_rss_feed(jobs)

    save_rss_feed(rss_feed, 'aiib_jobs.xml')
    print("Done!")


if __name__ == "__main__":
    main()
