"""main.py — Pipeline entry point.

Usage
-----
  python main.py --mode scrape "restaurants in Miami" --limit 50
  python main.py --mode scrape --queries-file query_example.txt
  python main.py --mode enrich --input data/output.csv
  python main.py --mode full   --queries-file query_example.txt --output-file data/leads.csv
  python main.py --mode full   --queries-file query_example.txt --no-web-scraping

The original CLI (mapScraperX.py) is unchanged and continues to work as before.
"""
import argparse
import logging
import sys


def _read_queries(file_path: str) -> list[str]:
    try:
        with open(file_path, encoding='utf-8') as fh:
            return [ln.strip() for ln in fh if ln.strip() and not ln.startswith('#')]
    except FileNotFoundError:
        print(f"Error: queries file not found: {file_path}")
        sys.exit(1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='mapScraper pipeline — Google Maps scraping + lead enrichment.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes
-----
  scrape   Run the Google Maps scraper only (same output as mapScraperX.py).
  enrich   Load an existing CSV and add features + lead scores.
  full     Scrape, then enrich the result.

Examples
--------
  # Scrape a single query
  python main.py --mode scrape "marketing agencies in New York" --limit 50

  # Scrape multiple queries from a file
  python main.py --mode scrape --queries-file query_example.txt

  # Enrich a previously generated CSV
  python main.py --mode enrich --input data/output.csv

  # Skip website scraping (faster, offline-friendly)
  python main.py --mode enrich --input data/output.csv --no-web-scraping

  # Full pipeline in one command
  python main.py --mode full --queries-file query_example.txt --output-file data/leads.csv
        """,
    )

    parser.add_argument(
        '--mode',
        choices=['scrape', 'enrich', 'full'],
        default='scrape',
        help='Pipeline mode (default: scrape)',
    )

    # --- scraping arguments ---------------------------------------------------
    query_group = parser.add_mutually_exclusive_group()
    query_group.add_argument(
        'query', nargs='?', type=str,
        help='Single search query (scrape / full modes)',
    )
    query_group.add_argument(
        '--queries-file', type=str, metavar='FILE',
        help='Text file with one search query per line',
    )
    parser.add_argument('--lang', type=str, default='en', metavar='CODE',
                        help='Language code (default: en)')
    parser.add_argument('--country', type=str, default='us', metavar='CODE',
                        help='Country code (default: us)')
    parser.add_argument('--limit', type=int, default=None, metavar='N',
                        help='Max results per query (default: no limit)')
    parser.add_argument('--output-file', type=str, default='data/output.csv',
                        metavar='PATH',
                        help='Raw scrape output CSV (default: data/output.csv)')
    parser.add_argument('--concurrent', type=int, default=3, metavar='N',
                        help='Concurrent scraper tasks (default: 3)')

    # --- enrichment arguments -------------------------------------------------
    parser.add_argument('--input', type=str, metavar='PATH',
                        help='Input CSV for enrich mode')
    parser.add_argument('--no-web-scraping', action='store_true',
                        help='Skip fetching lead websites during enrichment')
    parser.add_argument('--web-concurrent', type=int, default=10, metavar='N',
                        help='Concurrent website fetch tasks (default: 10)')
    parser.add_argument('--web-batch-size', type=int, default=100, metavar='N',
                        help='Rows per website-scraping batch (default: 100)')
    parser.add_argument('--web-timeout', type=int, default=10, metavar='SEC',
                        help='Per-request timeout for website fetches (default: 10)')

    # --- logging --------------------------------------------------------------
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging verbosity (default: INFO)',
    )

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s %(levelname)-8s %(name)s — %(message)s',
        datefmt='%H:%M:%S',
    )

    from pipeline.orchestrator import run_pipeline

    queries: list[str] = []
    if args.mode in ('scrape', 'full'):
        if args.query:
            queries = [args.query]
        elif args.queries_file:
            queries = _read_queries(args.queries_file)
        else:
            parser.error(f"--mode {args.mode} requires a query or --queries-file.")

    run_pipeline(
        mode=args.mode,
        queries=queries,
        lang=args.lang,
        country=args.country,
        limit=args.limit,
        max_concurrent=args.concurrent,
        input_path=args.input,
        output_file=args.output_file,
        scrape_websites=not args.no_web_scraping,
        web_concurrent=args.web_concurrent,
        web_batch_size=args.web_batch_size,
        web_timeout=args.web_timeout,
    )


if __name__ == '__main__':
    main()
