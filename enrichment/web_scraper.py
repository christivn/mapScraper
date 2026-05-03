"""Lightweight async website scraper for the enrichment pipeline.

Fetches the homepage of each lead's website and extracts simple signals:
- presence of contact / services pages
- basic keyword extraction
- heuristic for modern JS frameworks

All failures are caught and return an empty signal dict so the pipeline
never crashes due to a single unreachable domain.
"""
import asyncio
import logging
import re
from typing import Dict, List

import aiohttp

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False

logger = logging.getLogger(__name__)

_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

_CONTACT_KW = frozenset(['contact', 'contacto', 'kontakt', 'reach us', 'get in touch', 'reach out'])
_SERVICE_KW = frozenset([
    'services', 'products', 'solutions', 'offerings', 'portfolio',
    'what we do', 'our work', 'capabilities', 'servicios', 'productos',
])
_MODERN_SIGNALS = ['__next', '__nuxt', 'react', 'vue', 'angular', 'gatsby', 'svelte']
_WORD_RE = re.compile(r'\b[a-z]{4,15}\b')

_EMPTY_RESULT: Dict = {
    'web_has_contact': False,
    'web_has_services': False,
    'web_keywords': '',
    'web_is_modern': False,
    'web_scraped': False,
}

_STOP_WORDS = frozenset([
    'that', 'this', 'with', 'have', 'from', 'they', 'will', 'been',
    'your', 'more', 'were', 'when', 'there', 'their', 'what', 'about',
    'which', 'also', 'into', 'than', 'then', 'some', 'make', 'just',
    'like', 'time', 'know', 'take', 'year', 'good', 'people', 'come',
])


async def _fetch(session: aiohttp.ClientSession, url: str, timeout: int) -> str | None:
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    try:
        async with session.get(
            url,
            headers=_HEADERS,
            timeout=aiohttp.ClientTimeout(total=timeout),
            ssl=False,
            allow_redirects=True,
            max_redirects=5,
        ) as resp:
            if resp.status == 200:
                return await resp.text(errors='replace')
            logger.debug("[%s] HTTP %d", url, resp.status)
    except Exception as exc:
        logger.debug("[%s] fetch failed: %s", url, exc)
    return None


def _analyze(html: str) -> Dict:
    if _BS4_AVAILABLE:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True).lower()
    else:
        # Fallback: strip tags with regex
        text = re.sub(r'<[^>]+>', ' ', html).lower()

    html_lower = html.lower()

    has_contact = any(kw in text for kw in _CONTACT_KW)
    has_services = any(kw in text for kw in _SERVICE_KW)
    is_modern = any(sig in html_lower for sig in _MODERN_SIGNALS)

    words = _WORD_RE.findall(text)
    freq: Dict[str, int] = {}
    for w in words:
        if w not in _STOP_WORDS:
            freq[w] = freq.get(w, 0) + 1
    top = sorted(freq, key=freq.get, reverse=True)[:10]  # type: ignore[arg-type]

    return {
        'web_has_contact': has_contact,
        'web_has_services': has_services,
        'web_keywords': ', '.join(top),
        'web_is_modern': is_modern,
        'web_scraped': True,
    }


async def _enrich_one(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
    timeout: int,
) -> Dict:
    if not url or not url.strip():
        return dict(_EMPTY_RESULT)
    async with semaphore:
        html = await _fetch(session, url.strip(), timeout)
        if html:
            return _analyze(html)
        return dict(_EMPTY_RESULT)


async def _run_batch(
    urls: List[str],
    max_concurrent: int,
    timeout: int,
) -> List[Dict]:
    semaphore = asyncio.Semaphore(max_concurrent)
    connector = aiohttp.TCPConnector(ssl=False, limit=max_concurrent + 5)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [_enrich_one(session, url, semaphore, timeout) for url in urls]
        return await asyncio.gather(*tasks)


def enrich_websites(
    urls: List[str],
    *,
    max_concurrent: int = 10,
    batch_size: int = 100,
    timeout: int = 10,
) -> List[Dict]:
    """Enrich a list of URLs with website signals.

    Processes in batches to keep memory bounded for large inputs.
    Never raises — failed URLs return empty signal dicts.
    """
    if not _BS4_AVAILABLE:
        logger.warning(
            "beautifulsoup4 not installed — falling back to regex HTML stripping. "
            "Install it with: pip install beautifulsoup4"
        )

    results: List[Dict] = []
    total = len(urls)
    for batch_start in range(0, total, batch_size):
        batch = urls[batch_start: batch_start + batch_size]
        batch_num = batch_start // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        logger.info("Web scraping batch %d/%d (%d URLs)", batch_num, total_batches, len(batch))
        batch_results = asyncio.run(_run_batch(batch, max_concurrent, timeout))
        results.extend(batch_results)
    return results
