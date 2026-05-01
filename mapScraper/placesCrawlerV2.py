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
      [37][1]         int    – review count
      [39]            str    – full address
      [78]            str    – ChIJ place ID
      [178][0][1][0][0] str  – local phone (e.g. "(716) 847-0070")
      [178][0][1][1][0] str  – international phone (e.g. "+1 716-847-0070")
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
        'reviews': _safe_get(result, 37, 1, default=''),
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


async def _get_search_url(session, query, lang, country):
    """
    Step 1: GET /maps/search/{query} and extract the canonical pb= search URL
    from the <link> tag in the Maps SPA page.
    Returns the full search URL string, or None on failure.
    Called once per query; the returned URL is reused across all paginated pages.
    """
    encoded_query = quote(query)
    maps_url = f'https://www.google.com/maps/search/{encoded_query}?hl={lang}&gl={country}'

    try:
        async with session.get(maps_url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.error(f'[{query}] Maps page returned HTTP {resp.status}')
                return None
            html = await resp.text()
    except Exception as e:
        logger.error(f'[{query}] Failed to fetch Maps page: {e}')
        return None

    pb_match = re.search(r'href="(/search\?tbm=map[^"]+)"', html)
    if not pb_match:
        logger.error(
            f'[{query}] Could not find pb= search URL in Maps page. '
            f'Response may be a consent wall or bot-detection page. '
            f'HTML snippet: {html[:300]!r}'
        )
        return None

    search_path = pb_match.group(1).replace('&amp;', '&')
    search_url = 'https://www.google.com' + search_path
    logger.debug(f'[{query}] Search URL: {search_url[:120]}...')
    return search_url


async def _fetch_results_page(session, search_url, query, start=0):
    """
    Step 2: Fetch one page of tbm=map results.
    Appends &start=N to the base search URL for pages beyond the first.
    Returns a list of place dicts, or [] when there are no more results or on error.
    """
    url = search_url if start == 0 else f'{search_url}&start={start}'

    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            if resp.status != 200:
                logger.error(f'[{query}] tbm=map API returned HTTP {resp.status} (start={start})')
                return []
            raw = await resp.text()
    except Exception as e:
        logger.error(f'[{query}] Failed to fetch search results (start={start}): {e}')
        return []

    # Strip the XSSI prefix )]}' that Google prepends to JSON responses
    if raw.startswith(")]}'"):
        raw = raw[4:].strip()
    else:
        logger.error(
            "[%s] Unexpected response format (missing )]}' prefix) at start=%d. First 80 chars: %r",
            query, start, raw[:80]
        )
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.error(f'[{query}] JSON parse error at start={start}: {e}. First 200 chars: {raw[:200]!r}')
        return []

    # Results live at data[64]; each entry is [None, <place-data-list>]
    results_array = _safe_get(data, 64)
    if results_array is None:
        logger.debug(
            f'[{query}] data[64] is missing at start={start}. '
            f'Top-level array length: {len(data) if isinstance(data, list) else "N/A"}.'
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

    logger.debug(f'[{query}] Extracted {len(places)} places from page (start={start})')
    return places


async def search_async(query, lang, country, limit, semaphore):
    """Async search with semaphore-based rate limiting and multi-page pagination."""
    result = []
    pbar = tqdm(desc=f"Scraping '{query[:30]}'", unit='results', leave=False)

    async with semaphore:
        try:
            connector = aiohttp.TCPConnector(ssl=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                # Step 1: resolve the pb= search URL once for all pages
                search_url = await _get_search_url(session, query, lang, country)
                if not search_url:
                    logger.warning(f'[{query}] Could not obtain search URL.')
                    pbar.set_postfix({'status': 'no-url'})
                    pbar.close()
                    return result

                # Step 2: paginate — each page adds ~20 results via &start=N
                page_size = 20
                start = 0
                while True:
                    places = await _fetch_results_page(session, search_url, query, start)

                    if not places:
                        # Empty page means no more results available
                        logger.debug(f'[{query}] Empty page at start={start}, stopping.')
                        break

                    for place in places:
                        result.append(place)
                        pbar.update(1)
                        pbar.set_postfix({'Total': len(result)})
                        if limit and len(result) >= limit:
                            break

                    if limit and len(result) >= limit:
                        break

                    start += page_size

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
