"""
Google Maps Places Scraper - Async HTTP-based implementation
Based on a new logic but adapted to the existing structure.
"""

import logging
import re
import asyncio
import aiohttp
from urllib.parse import quote, unquote, urlparse, parse_qs
from lxml import html
from lxml.html import HtmlElement
from typing import List, Dict, Optional, Tuple
import phonenumbers

logger = logging.getLogger(__name__)


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
}


def extract_phone(text: str) -> str:
    """Extract phone number from text using regex."""
    if not text:
        return ''
    
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    matches = re.findall(phone_regex, text)
    
    if not matches:
        return ''
    
    for match in matches:
        digits = re.sub(r'\D', '', match)
        if len(digits) < 8:
            continue
        try:
            parsed = phonenumbers.parse(match, None)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except:
            pass
        return match.strip()
    return ''



# Contact-info extraction pipeline


# Regex used to split raw phone strings into individual numbers.
_PHONE_SPLIT_PATTERN = re.compile(r'(?:\s{2,}|\u00A0{2,}|,|\|/)')

# Leading junk stripped after removing the label text from an ancestor's content.
_LABEL_STRIP_PATTERN = re.compile(r'^[\s:,-]+')


def _extract_element_text(element: Optional[HtmlElement]) -> str:
    """Return the full text content of an lxml element, or an empty string.

    Handles both ``HtmlElement`` instances (via ``text_content()``) and bare
    elements that only expose ``.text``.
    """
    if element is None:
        return ''

    if hasattr(element, 'text_content'):
        return element.text_content().strip()

    return (element.text or '').strip()


def _resolve_label_value(
    doc: HtmlElement,
    label_name: str,
) -> Optional[str]:
    """Walk the DOM ancestor chain of *label_name* to extract its associated value.

    Strategy (unchanged from original):
        1. Locate the first element whose *normalised* text equals ``label_name``.
        2. Traverse up through parent → grandparent → great-grandparent.
        3. For each ancestor, extract full text, strip the label, and return the
           first non-empty remainder.  The precedence is:
           **grandparent → parent → great-grandparent**.
    """
    xpath_expr = f"//*[normalize-space(text())='{label_name}']"
    target_nodes = doc.xpath(xpath_expr)

    if not target_nodes:
        return None

    target_node = target_nodes[0]

    # Build the ancestor chain (parent → grandparent → great-grandparent).
    parent = target_node.getparent()
    grandparent = parent.getparent() if parent is not None else None
    great_grandparent = grandparent.getparent() if grandparent is not None else None

    # Ordered by lookup priority: grandparent, parent, great-grandparent.
    ancestors = (grandparent, parent, great_grandparent)

    for ancestor in ancestors:
        text = _extract_element_text(ancestor)

        if not text or label_name not in text:
            continue

        cleaned = text.replace(label_name, '')
        cleaned = _LABEL_STRIP_PATTERN.sub('', cleaned).strip()

        if cleaned:
            return cleaned

    return None


def _parse_phone_numbers(raw_value: str) -> List[str]:
    """Split a raw phone string into individual cleaned numbers.

    Splits on double-spaces, non-breaking spaces, commas, pipes, or slashes —
    exactly matching the original behaviour.
    """
    parts = _PHONE_SPLIT_PATTERN.split(raw_value)
    return [part.strip() for part in parts if part.strip()]


def _extract_fallback_website(doc: HtmlElement) -> Optional[str]:
    """Extract website from the fallback HTML payload."""
    xpath_expr = "//span[text()='Website']/ancestor::a[1]/@href"
    nodes = doc.xpath(xpath_expr)
    if nodes:
        return str(nodes[0]).strip()
    return None


def extract_contact_info(raw_payload: str) -> Dict:
    """Extract address and phone numbers from an HTML payload.

    Parses the raw HTML using ``lxml`` and walks the DOM to locate labelled
    contact fields (``Address``, ``Phone``).  Returns a plain dict for
    backward-compatibility with existing callers.

    Args:
        raw_payload: Raw HTML string (e.g. from Google's async detail endpoint).

    Returns:
        A dictionary with keys ``address`` (``str | None``) and
        ``phone_numbers`` (``list[str]``).
    """
    try:
        doc = html.fromstring(raw_payload)
    except Exception:
        logger.warning("Failed to parse HTML payload for contact extraction", exc_info=True)
        return {'address': None, 'phone_numbers': [], 'website': None}

    address = _resolve_label_value(doc, 'Address')

    phone_raw = _resolve_label_value(doc, 'Phone')
    phone_numbers = _parse_phone_numbers(phone_raw) if phone_raw else []

    website = _extract_fallback_website(doc)

    return {'address': address, 'phone_numbers': phone_numbers, 'website': website}


async def fetch_extra_details(session: aiohttp.ClientSession, query: str, cid: str, timeout: int = 15) -> Optional[str]:
    """Fetch extra details from Google's async endpoint."""
    url = f"https://www.google.com/async/lcl_akp?q={quote(query)}&async=ludocids:{cid},_fmt:prog"
    
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"HTTP {response.status} for CID {cid}")
                return None
    except asyncio.TimeoutError:
        print(f"Timeout fetching extra details for CID {cid}")
        return None
    except Exception as e:
        print(f"Error fetching extra details for CID {cid}: {e}")
        return None


async def fetch_page(session: aiohttp.ClientSession, url: str, timeout: int = 20) -> Optional[str]:
    """Fetch a single page with proper headers."""
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"HTTP {response.status} for {url}")
                return None
    except asyncio.TimeoutError:
        print(f"Timeout fetching {url}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_search_results(html_content: str) -> List[Dict]:
    """Parse search results from HTML content."""
    scraped_data = []
    
    try:
        doc = html.fromstring(html_content)
    except Exception as e:
        print(f"Failed to parse HTML: {e}")
        return scraped_data
    
    # Find search results container
    search_div = doc.xpath("//div[@id='search']")
    if not search_div:
        return scraped_data
    
    search_div = search_div[0]
    items = search_div.xpath(".//div[contains(@class, 'VkpGBb')]")
    
    if not items:
        return scraped_data
    
    for item in items:
        row = {
            'title': 'N/A',
            'cid': '',
            'stars': 0,
            'reviews': 0,
            'category': '',
            'address': '',
            'completePhoneNumber': '',
            'url': '',
            'place_id': ''
        }
        
        # --- 0. EXTRACT DATA-CID ---
        cid_elements = item.xpath(".//@data-cid")
        if cid_elements:
            row['cid'] = cid_elements[0]

        # Fallback 1: data-ludocid attribute
        if not row['cid']:
            ludocid_elements = item.xpath(".//@data-ludocid")
            if ludocid_elements:
                row['cid'] = ludocid_elements[0]

        # Fallback 2: ludocid param from any link within the card
        if not row['cid']:
            for link in item.xpath(".//a/@href"):
                if 'ludocid=' in link:
                    match = re.search(r'ludocid=(\d+)', link)
                    if match:
                        row['cid'] = match.group(1)
                        break
        
        # Extract title
        heading = item.xpath(".//*[@role='heading']")
        if heading:
            row['title'] = ' '.join(heading[0].text_content().split())
        
        # --- 1. NEW STRATEGY: ADDRESS FROM DIRECTIONS URL ---
        all_links = item.xpath(".//a")
        directions_link = None
        for link in all_links:
            href = link.get('href', '')
            if href.startswith('/maps/dir/'):
                directions_link = link
                break
        
        if directions_link is not None:
            href = directions_link.get('href', '')
            try:
                if '/data=' in href:
                    dest_segment = href.split('/data=')[0].split('/')[-1]
                else:
                    dest_segment = href.split('/')[-1]
                
                if dest_segment:
                    full_address = unquote(dest_segment.replace('+', ' ')).strip()
                    full_address = html.fromstring(f"<div>{full_address}</div>").text_content()
                    
                    if row['title'] and row['title'] != 'N/A':
                        if full_address.startswith(row['title']):
                            full_address = full_address[len(row['title']):].lstrip(', -').strip()
                        elif full_address.endswith(row['title']):
                            full_address = full_address[:-len(row['title'])].rstrip(', -').strip()
                    
                    row['address'] = full_address
            except Exception as e:
                pass
        
        # --- 2. WEBSITE EXTRACTION ---
        website_link = None
        for link in all_links:
            link_text = link.text_content().lower() if link.text_content() else ''
            href = link.get('href', '')
            if 'website' in link_text and href.startswith('http'):
                website_link = link
                break
        
        if website_link:
            row['url'] = website_link.get('href', '')
        
        # --- 3. TEXT PARSING ---
        details_div = item.xpath(".//div[contains(@class, 'rllt__details')]")
        if details_div:
            details_div = details_div[0]
            
            # Get all divs in details
            lines = details_div.xpath(".//div")
            
            for line in lines:
                # Skip headings
                if line.get('role') == 'heading' or line.xpath(".//*[@role='heading']"):
                    continue
                
                text = ' '.join(line.text_content().split()).strip()
                if not text:
                    continue
                
                # Check for rating line
                has_stars = line.xpath(".//*[contains(@class, 'yi40Hd')]") or line.xpath(".//*[@aria-hidden='true']") or re.match(r'^\d\.\d', text)
                
                if has_stars:
                    star_span = line.xpath(".//*[contains(@class, 'yi40Hd')]//text() | //*[@aria-hidden='true']//text()")
                    if star_span:
                        try:
                            row['stars'] = float(star_span[0].strip())
                        except:
                            pass
                    
                    review_span = line.xpath(".//*[contains(@aria-label, 'reviews')]//text() | .//*[contains(@class, 'RDApEe')]//text()")
                    if review_span:
                        try:
                            row['reviews'] = int(re.sub(r'\D', '', review_span[0]))
                        except:
                            pass
                    
                    if '·' in text:
                        parts = text.split('·')
                        row['category'] = parts[-1].strip()
                    
                    continue
                
                # Check for status or feature lines
                status_keywords = ['Opens', 'Closed', 'Open 24 hours', 'Dine-in', 'Takeout', 'Delivery']
                is_status_or_feature = any(kw in text for kw in status_keywords)
                is_quote = 'pJ3Ci' in line.get('class', '')
                
                if is_status_or_feature or is_quote:
                    continue
                
                # Split by middle dot
                segments = [s.strip() for s in text.split('·')]
                
                for segment in segments:
                    if 'years in business' in segment:
                        continue
                    
                    phone = extract_phone(segment)
                    looks_like_phone = bool(re.match(r'^[\d\s\-\+\(\)]{8,}$', segment))
                    
                    if phone:
                        row['completePhoneNumber'] = phone
                    elif not looks_like_phone and len(segment) > 3 and not row['address']:
                        row['address'] = segment
        
        scraped_data.append(row)
    
    return scraped_data


async def search_single(
    session: aiohttp.ClientSession,
    query: str,
    lang: str = 'en',
    country: str = 'us',
    mode: str = 'standard',
    limit: int = 0
) -> List[Dict]:
    """
    Search for a single query with different modes.
    
    Modes:
    - fast: Main search only, no phone fallback
    - standard: Skip phone fallback if ANY result has a phone number (faster)
    - complete: Always run phone fallback for missing numbers (thorough)
    """
    full_list = []
    pagination = 0
    
    # Phase 1: Main Search Loop
    while True:
        url = f"https://www.google.com/search?q={quote(query)}&start={pagination}&udm=1&hl={quote(lang)}&gl={quote(country)}"
        print(f"Fetching Search Page: {url}")
        
        html_content = await fetch_page(session, url)
        
        if not html_content:
            break
        
        results = parse_search_results(html_content)
        
        if results:
            pagination += 10
            full_list.extend(results)
            
            if limit > 0 and len(full_list) >= limit:
                full_list = full_list[:limit]
                break
        else:
            break
    
    # Deduplicate by cid or title+address
    seen = set()
    unique_results = []
    for item in full_list:
        key = item.get('cid') or (item.get('title', '') + item.get('address', ''))
        if key and key not in seen:
            seen.add(key)
            unique_results.append(item)
    
    # Phase 2: Missing Phone Number Fallback (Standard & Complete modes)
    if mode in ('standard', 'complete'):
        # Standard mode: skip fallback if any phone exists, otherwise fallback
        # Complete mode: always fallback (phone + address)
        
        if mode == 'standard':
            any_phone = any(item.get('completePhoneNumber') for item in unique_results)
            if any_phone:
                print(f"Skipping phone fallback - at least one result has a phone number")
            else:
                print("No phone numbers found in main search, proceeding with fallback...")
        
        # Run fallback for complete mode OR for standard when no phones exist
        should_fallback = (mode == 'complete') or not any(
            item.get('completePhoneNumber') for item in unique_results
        )
        
        if should_fallback:
            for item in unique_results:
                if not item.get('completePhoneNumber') and item.get('cid'):
                    print(f"Missing phone for '{item.get('title')}'. Fetching details via CID: {item.get('cid')}...")
                    
                    raw_payload = await fetch_extra_details(session, query, item.get('cid'))
                    
                    if raw_payload:
                        try:
                            extra_info = extract_contact_info(raw_payload)
                            
                            if extra_info.get('phone_numbers') and len(extra_info['phone_numbers']) > 0:
                                item['completePhoneNumber'] = extra_info['phone_numbers'][0]
                            
                            # Complete mode also updates address from extra info
                            if mode == 'complete' and extra_info.get('address') and not item.get('address'):
                                item['address'] = extra_info['address']

                            if extra_info.get('website') and not item.get('url'):
                                item['url'] = extra_info['website']
                        except Exception as e:
                            print(f"Failed to parse extra info for CID {item.get('cid')}: {e}")
    
    return unique_results


async def search_multiple(
    queries: List[str],
    lang: str = 'en',
    country: str = 'us',
    limit_per_query: int = 0,
    max_concurrent: int = 3,
    mode: str = 'standard'
) -> List[Dict]:
    """
    Search multiple queries concurrently.
    """
    connector = aiohttp.TCPConnector(limit=max_concurrent)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [search_single(session, query, lang, country, mode, limit_per_query) for query in queries]
        results = await asyncio.gather(*tasks)
    
    # Flatten results
    all_results = []
    for result in results:
        all_results.extend(result)
    
    return all_results


def search(query: str, lang: str = 'en', country: str = 'us', limit: int = 0, mode: str = 'standard') -> List[Dict]:
    """
    Synchronous wrapper for search_single.
    """
    async def _run():
        connector = aiohttp.TCPConnector(limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            return await search_single(session, query, lang, country, mode, limit)
    
    return asyncio.run(_run())


def search_multiple_sync(
    queries: List[str],
    lang: str = 'en',
    country: str = 'us',
    limit_per_query: int = 0,
    max_concurrent: int = 3,
    mode: str = 'standard'
) -> List[Dict]:
    """
    Synchronous wrapper for search_multiple.
    """
    return asyncio.run(search_multiple(queries, lang, country, limit_per_query, max_concurrent, mode))


def save_to_csv(results: List[Dict], filename: str = 'data/output.csv'):
    """Save results to CSV file."""
    import csv
    
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    if not results:
        print("No results to save.")
        return
    
    fieldnames = ['id', 'gmap_url', 'title', 'category', 'address', 'phoneNumber',
                  'additionalPhoneNumbers', 'website', 'stars', 'reviews']
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in results:
            phone_numbers = item.get('phone_numbers', [])
            primary_phone = item.get('completePhoneNumber', '')
            additional = [p for p in phone_numbers if p != primary_phone]

            row = {
                'id': item.get('cid', ''),
                'gmap_url': f"https://www.google.com/maps?cid={item.get('cid', '')}" if item.get('cid') else '',
                'title': item.get('title', ''),
                'category': item.get('category', ''),
                'address': item.get('address', ''),
                'phoneNumber': primary_phone,
                'additionalPhoneNumbers': '|'.join(additional),
                'website': item.get('url', ''),
                'stars': item.get('stars', 0),
                'reviews': item.get('reviews', 0)
            }
            
            writer.writerow(row)
    
    print(f"Saved {len(results)} results to {filename}")