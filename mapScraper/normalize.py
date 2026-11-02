"""Schema conversion: Google Search results → internal-API (placesCrawlerV2) schema."""
from urllib.parse import urlparse
from typing import List


def normalize_search_results(rows: List[dict]) -> List[dict]:
    """Map Google Search results (places_crawler) onto the internal-API schema.

    places_crawler rows carry cid/title/category/address/completePhoneNumber/url
    but lack several of the pipeline's required columns; fill those in so the
    shared CSV writer and the enrichment step accept them unchanged.
    """
    normalized = []
    for row in rows:
        url = row.get('url', '') or ''
        cid = row.get('cid', '') or row.get('place_id', '') or ''
        title = row.get('title', '') or ''
        if title == 'N/A':
            title = ''
        normalized.append({
            'id': cid,
            'url_place': f'https://www.google.com/maps?cid={cid}' if cid else '',
            'title': title,
            'category': row.get('category', '') or '',
            'address': row.get('address', '') or '',
            'phoneNumber': '',
            'completePhoneNumber': row.get('completePhoneNumber', '') or '',
            'domain': urlparse(url).netloc if url else '',
            'url': url,
            'coor': '',
            'stars': row.get('stars', ''),
            'reviews': row.get('reviews', ''),
            'source_query': row.get('source_query', '') or '',
        })
    return normalized
