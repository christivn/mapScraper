import asyncio
import aiohttp
from urllib.parse import quote
import json
import csv
import re
import logging
from tqdm import tqdm

logger = logging.getLogger(__name__)

# Realistic browser headers to avoid bot detection
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def _safe_get(obj, *indices, default=None):
    """Safely navigate nested lists/dicts, returning default on any failure."""
    try:
        for idx in indices:
            obj = obj[idx]
        return obj
    except (IndexError, TypeError, KeyError):
        return default


def _extract_place(result, query):
    """
    Extract a place dict from a single result entry (data[64][i][1]).

    The tbm=map JSON structure (as of 2026) embeds per-place data in a
    ~260-element list.  Key offsets:
      [4][7]          float  – average star rating
      [7][0]          str    – website URL
      [7][1]          str    – website domain
      [9][2], [9][3]  float  – latitude, longitude
      [11]            str    – place name
      [13][0]         str    – primary category
      [39]            str    – full address
      [78]            str    – ChIJ place ID
      [178][0][1][0][0] str  – local phone (e.g. "(716) 847-0070")
      [178][0][1][1][0] str  – international phone (e.g. "+1 716-847-0070")

    NOTE: review count is not present in the tbm=map search response.
    """
    place_id = _safe_get(result, 78)
    if not place_id:
        logger.debug('Skipping result with no place ID')
        return None

    obj = {
        'id': place_id,
        'url_place': f'https://www.google.com/maps/place/?q=place_id:{place_id}',
        'title': _safe_get(result, 11, default=''),
        'category': _safe_get(result, 13, 0, default=''),
        'address': _safe_get(result, 39, default=''),
        'phoneNumber': '',
        'completePhoneNumber': '',
        'domain': _safe_get(result, 7, 1, default=''),
        'url': _safe_get(result, 7, 0, default=''),
        'coor': '',
        'stars': _safe_get(result, 4, 7, default=''),
        'reviews': '',   # not available in tbm=map response
        'source_query': query,
    }

    # Phone numbers
    phone_local = _safe_get(result, 178, 0, 1, 0, 0)
    phone_intl = _safe_get(result, 178, 0, 1, 1, 0)
    if phone_local:
        obj['phoneNumber'] = phone_local
    if phone_intl:
        obj['completePhoneNumber'] = phone_intl

    # Coordinates
    lat = _safe_get(result, 9, 2)
    lng = _safe_get(result, 9, 3)
    if lat is not None and lng is not None:
        obj['coor'] = f'{lat},{lng}'

    return obj


async def _fetch_page(session, query, lang, country):
    """
    Two-step fetch:
      1. GET /maps/search/{query} → extract the canonical pb= search URL
      2. GET /search?tbm=map&...&pb=... → parse )]}'-prefixed JSON

    Returns list of raw place dicts, or [] on any failure.
    """
    encoded_query = quote(query)
    maps_url = f'https://www.google.com/maps/search/{encoded_query}?hl={lang}&gl={country}'

    # Step 1 – Maps SPA page (just for the pb= URL in the <link> tag)
    try:
        async with session.get(maps_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.error(f'[{query}] Maps page returned HTTP {resp.status}')
                return []
            html = await resp.text()
    except Exception as e:
        logger.error(f'[{query}] Failed to fetch Maps page: {e}')
        return []

    pb_match = re.search(r'href="(/search\?tbm=map[^"]+)"', html)
    if not pb_match:
        logger.error(
            f'[{query}] Could not find pb= search URL in Maps page. '
            f'Response may be a consent wall or bot-detection page. '
            f'HTML snippet: {html[:300]!r}'
        )
        return []

    search_path = pb_match.group(1).replace('&amp;', '&')
    search_url = 'https://www.google.com' + search_path
    logger.debug(f'[{query}] Search URL: {search_url[:120]}...')

    # Step 2 – JSON search results
    try:
        async with session.get(search_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.error(f'[{query}] tbm=map API returned HTTP {resp.status}')
                return []
            raw = await resp.text()
    except Exception as e:
        logger.error(f'[{query}] Failed to fetch search results: {e}')
        return []

    # Strip the XSSI prefix )]}' that Google prepends to JSON responses
    if raw.startswith(")]}'"):
        raw = raw[4:].strip()
    else:
        logger.error(
            "[%s] Unexpected response format (missing )]}' prefix). First 80 chars: %r",
            query, raw[:80]
        )
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f'[{query}] JSON parse error: {e}. First 200 chars: {raw[:200]!r}')
        return []

    # Results live at data[64]; each entry is [None, <place-data-list>]
    results_array = _safe_get(data, 64)
    if results_array is None:
        logger.error(
            f'[{query}] data[64] is missing. Top-level array length: '
            f'{len(data) if isinstance(data, list) else "N/A"}. '
            f'Google may have changed the response structure.'
        )
        return []

    places = []
    for i, entry in enumerate(results_array):
        if entry is None or not isinstance(entry, list) or len(entry) < 2:
            logger.debug(f'[{query}] Skipping malformed entry at index {i}')
            continue
        result = entry[1]
        if result is None or not isinstance(result, list):
            logger.debug(f'[{query}] Skipping entry[1]=None at index {i}')
            continue
        try:
            place = _extract_place(result, query)
            if place:
                places.append(place)
        except Exception as e:
            logger.warning(f'[{query}] Error extracting result {i}: {e}')

    logger.debug(f'[{query}] Extracted {len(places)} places from page')
    return places


async def search_async(query, lang, country, limit, semaphore):
    """Async search with semaphore-based rate limiting."""
    result = []
    pbar = tqdm(desc=f"Scraping '{query[:30]}'", unit='results', leave=False)

    async with semaphore:
        try:
            connector = aiohttp.TCPConnector(ssl=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                places = await _fetch_page(session, query, lang, country)

                if not places:
                    logger.warning(f'[{query}] No results returned.')
                    pbar.set_postfix({'status': 'empty'})
                else:
                    for place in places:
                        result.append(place)
                        pbar.update(1)
                        pbar.set_postfix({'Total': len(result)})
                        if limit and len(result) >= limit:
                            break

        except Exception as e:
            logger.error(f'[{query}] Unhandled exception: {e}')
            pbar.set_postfix({'Error': str(e)[:30]})

    pbar.close()
    logger.info(f'[{query}] Done — {len(result)} result(s)')
    return result


async def search_multiple_async(queries, lang, country, limit, max_concurrent=3):
    """Search multiple queries concurrently with rate limiting."""
    semaphore = asyncio.Semaphore(max_concurrent)
    tasks = [search_async(query, lang, country, limit, semaphore) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error in query '{queries[i]}': {result}")
        else:
            all_results.extend(result)

    return all_results


def search(query, lang, country, limit):
    """Synchronous wrapper for backward compatibility."""
    return asyncio.run(search_async(query, lang, country, limit, asyncio.Semaphore(1)))


def search_multiple(queries, lang, country, limit, max_concurrent=3):
    """Synchronous wrapper for multiple queries."""
    return asyncio.run(search_multiple_async(queries, lang, country, limit, max_concurrent))


def save_to_csv(data, filename='data/output.csv'):
    """Save place data to CSV file."""
    if not data:
        print('No data to save.')
        return

    column_order = [
        'id', 'url_place', 'title', 'category', 'address',
        'phoneNumber', 'completePhoneNumber', 'domain', 'url',
        'coor', 'stars', 'reviews', 'source_query',
    ]

    for record in data:
        for col in column_order:
            if col not in record:
                record[col] = ''

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=column_order)
            writer.writeheader()
            writer.writerows(data)
        print(f'Data saved to {filename}')
    except Exception as e:
        print(f'Error saving data to {filename}: {e}')
