"""Central pipeline orchestrator.

Exposes a single public function: run_pipeline(mode, ...)

Modes
-----
scrape  Run the Google Maps scraper only. Outputs a raw CSV.
enrich  Load an existing raw CSV, run enrichment, save an enriched CSV.
full    Scrape first, then enrich the result.

The scraper and the enrichment step are never executed simultaneously —
the orchestrator runs them sequentially within a single process.
"""
import logging
import os
from typing import List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Columns that must be present in any CSV handed to the enrichment step
_REQUIRED_COLUMNS = [
    'id', 'url_place', 'title', 'category', 'address',
    'phoneNumber', 'completePhoneNumber', 'domain', 'url',
    'coor', 'stars', 'reviews', 'source_query',
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _enriched_path(raw_path: str) -> str:
    base, ext = os.path.splitext(raw_path)
    return f"{base}_enriched{ext or '.csv'}"


def _load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    missing = [c for c in _REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Input CSV is missing required columns: {missing}. "
            f"Columns found: {list(df.columns)}"
        )
    logger.info("Loaded %d rows from %s", len(df), path)
    return df


def _run_scraper(
    queries: List[str],
    lang: str,
    country: str,
    limit: Optional[int],
    output_file: str,
    max_concurrent: int,
) -> None:
    import mapScraper.placesCrawlerV2 as crawler

    logger.info("Scraping %d queries → %s", len(queries), output_file)
    _ensure_dir(output_file)

    results = crawler.search_multiple(queries, lang, country, limit, max_concurrent)
    if not results:
        logger.warning("Scraper returned 0 results.")
    crawler.save_to_csv(results, output_file)
    logger.info("Scrape done: %d places saved to %s", len(results), output_file)


def _run_enrichment(
    df: pd.DataFrame,
    *,
    scrape_websites: bool,
    web_concurrent: int,
    web_batch_size: int,
    web_timeout: int,
) -> pd.DataFrame:
    from enrichment.features import engineer_features
    from enrichment.scoring import compute_scores

    logger.info("Engineering features …")
    df = engineer_features(df)

    if scrape_websites:
        from enrichment.web_scraper import enrich_websites
        urls = df['url'].fillna('').tolist()
        non_empty = sum(1 for u in urls if u.strip())
        logger.info("Scraping %d/%d websites …", non_empty, len(urls))
        web_rows = enrich_websites(
            urls,
            max_concurrent=web_concurrent,
            batch_size=web_batch_size,
            timeout=web_timeout,
        )
        web_df = pd.DataFrame(web_rows, index=df.index)
        df = pd.concat([df, web_df], axis=1)
    else:
        logger.info("Website scraping skipped (--no-web-scraping).")

    logger.info("Computing lead scores …")
    df = compute_scores(df)

    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_pipeline(
    mode: str,
    *,
    queries: Optional[List[str]] = None,
    lang: str = 'en',
    country: str = 'us',
    limit: Optional[int] = None,
    max_concurrent: int = 3,
    input_path: Optional[str] = None,
    output_file: str = 'data/output.csv',
    scrape_websites: bool = True,
    web_concurrent: int = 10,
    web_batch_size: int = 100,
    web_timeout: int = 10,
) -> None:
    """Execute the pipeline in the requested mode.

    Parameters
    ----------
    mode:             'scrape' | 'enrich' | 'full'
    queries:          Search queries (required for scrape / full).
    lang:             Google Maps language code.
    country:          Google Maps country code.
    limit:            Max results per query (None = no limit).
    max_concurrent:   Concurrent scraper tasks.
    input_path:       Path to an existing CSV (required for enrich mode).
    output_file:      Destination for the raw scrape CSV.
    scrape_websites:  Whether to fetch lead websites during enrichment.
    web_concurrent:   Concurrent website fetch tasks.
    web_batch_size:   Rows per website-scraping batch.
    web_timeout:      Per-request timeout (seconds) for website fetches.
    """
    mode = mode.lower().strip()

    if mode == 'scrape':
        if not queries:
            raise ValueError("'scrape' mode requires at least one query.")
        _run_scraper(queries, lang, country, limit, output_file, max_concurrent)

    elif mode == 'enrich':
        if not input_path:
            raise ValueError("'enrich' mode requires --input <path-to-csv>.")
        df = _load_csv(input_path)
        df = _run_enrichment(
            df,
            scrape_websites=scrape_websites,
            web_concurrent=web_concurrent,
            web_batch_size=web_batch_size,
            web_timeout=web_timeout,
        )
        out = _enriched_path(input_path)
        _ensure_dir(out)
        df.to_csv(out, index=False)
        logger.info("Enriched CSV saved to %s", out)
        print(f"Enriched CSV saved to: {out}")

    elif mode == 'full':
        if not queries:
            raise ValueError("'full' mode requires at least one query.")
        _run_scraper(queries, lang, country, limit, output_file, max_concurrent)
        df = _load_csv(output_file)
        df = _run_enrichment(
            df,
            scrape_websites=scrape_websites,
            web_concurrent=web_concurrent,
            web_batch_size=web_batch_size,
            web_timeout=web_timeout,
        )
        out = _enriched_path(output_file)
        _ensure_dir(out)
        df.to_csv(out, index=False)
        logger.info("Enriched CSV saved to %s", out)
        print(f"Raw CSV:      {output_file}")
        print(f"Enriched CSV: {out}")

    else:
        raise ValueError(
            f"Unknown mode '{mode}'. Valid modes: scrape, enrich, full."
        )
