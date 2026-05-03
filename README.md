![Header](https://github.com/christivn/mapScraper/blob/main/github-header-image.png?raw=true)

# Google Maps Scraper + Enrichment Pipeline

A Python tool for scraping Google Maps local services data **and** enriching the results with lead-scoring signals.

Two entry points, fully independent:

| Script | Purpose |
|--------|---------|
| `mapScraperX.py` | Original scraper CLI — unchanged, backward-compatible |
| `main.py` | New pipeline CLI with `scrape / enrich / full` modes |

---

## Features

### Scraping (original)
- Place ID, Maps URL, business name, category, full address
- Phone (local + international format)
- Website domain + URL
- GPS coordinates
- Average star rating + review count
- Concurrent async processing, configurable language / country

### Enrichment (new)
- Feature engineering from existing CSV columns
- Lightweight website scraping (contact page, service keywords, modern-stack detection)
- Interpretable lead scoring (0–100) with segment labels
- Works on any previously generated CSV — scraper never has to re-run

---

## Prerequisites

- Python 3.10+
- pip

## Installation

```bash
git clone https://github.com/christivn/mapScraper.git
cd mapScraper
pip install -r requirements.txt
```

Dependencies: `aiohttp`, `tqdm`, `pandas`, `beautifulsoup4`

---

## Usage — original scraper (mapScraperX.py)

Everything here works exactly as before.

```bash
# Single query
python mapScraperX.py "restaurants in Miami" --limit 50

# Multiple queries from file
python mapScraperX.py --queries-file query_example.txt

# With concurrency and custom output
python mapScraperX.py --queries-file query_example.txt \
  --lang en --country us --limit 25 \
  --output-file data/custom.csv --concurrent 5
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `query` | — | Single search query |
| `--queries-file FILE` | — | File with one query per line |
| `--lang CODE` | `en` | Language code |
| `--country CODE` | `us` | Country code |
| `--limit N` | no limit | Max results (total / per query) |
| `--output-file PATH` | `data/output.csv` | Output CSV path |
| `--concurrent N` | `3` | Max concurrent queries (3–5 recommended) |

---

## Usage — pipeline (main.py)

### Modes

| Mode | What it does |
|------|-------------|
| `scrape` | Google Maps scraping only — identical output to `mapScraperX.py` |
| `enrich` | Load an existing CSV → add features + lead scores → save enriched CSV |
| `full` | Scrape first, then enrich the result |

### Examples

```bash
# Scrape (same as mapScraperX.py)
python main.py --mode scrape "marketing agencies in New York" --limit 50
python main.py --mode scrape --queries-file query_example.txt

# Enrich a previously generated CSV
python main.py --mode enrich --input data/output.csv

# Enrich without fetching websites (faster, offline-safe)
python main.py --mode enrich --input data/output.csv --no-web-scraping

# Full pipeline in one command
python main.py --mode full \
  --queries-file query_example.txt \
  --output-file data/leads.csv

# Verbose debug output
python main.py --mode enrich --input data/output.csv --log-level DEBUG
```

### All options

```
--mode {scrape,enrich,full}   Pipeline mode (default: scrape)
query                          Single search query
--queries-file FILE            File with one query per line
--lang CODE                    Language code (default: en)
--country CODE                 Country code (default: us)
--limit N                      Max results per query
--output-file PATH             Raw scrape output (default: data/output.csv)
--concurrent N                 Concurrent scraper tasks (default: 3)
--input PATH                   Input CSV for enrich mode
--no-web-scraping              Skip website fetching during enrichment
--web-concurrent N             Concurrent website fetch tasks (default: 10)
--web-batch-size N             Rows per website-scraping batch (default: 100)
--web-timeout SEC              Per-request timeout for websites (default: 10)
--log-level {DEBUG,INFO,...}   Logging verbosity (default: INFO)
```

---

## Output format

### Raw scrape CSV (unchanged)

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Google Place ID | `ChIJN1t_tDeuEmsRUsoyG83frY4` |
| `url_place` | Google Maps link | `https://www.google.com/maps/place/?q=place_id:...` |
| `title` | Business name | `Joe's Pizza` |
| `category` | Business category | `Pizza restaurant` |
| `address` | Full address | `123 Main St, New York, NY 10001` |
| `phoneNumber` | Local phone | `(555) 123-4567` |
| `completePhoneNumber` | International phone | `+1 555-123-4567` |
| `domain` | Website domain | `joespizza.com` |
| `url` | Full website URL | `https://www.joespizza.com` |
| `coor` | Coordinates | `40.7128,-74.0060` |
| `stars` | Average rating | `4.5` |
| `reviews` | Review count | `234` |
| `source_query` | Original query | `pizza in New York` |

### Enriched CSV (all original columns plus)

| Column | Type | Description |
|--------|------|-------------|
| `has_phone` | bool | Phone number present |
| `has_website` | bool | Website domain or URL present |
| `domain_valid` | bool | Domain passes basic format validation |
| `rating_score` | float | `stars × log(reviews+1)` — penalises high ratings with few reviews |
| `review_density` | float | Normalised review count within the batch (0–1) |
| `web_has_contact` | bool | Contact page / section detected on the website |
| `web_has_services` | bool | Services / products section detected |
| `web_keywords` | str | Top 10 content keywords (comma-separated) |
| `web_is_modern` | bool | Modern JS framework detected (React, Vue, Next.js, …) |
| `web_scraped` | bool | Whether the website was reachable and scraped |
| `score` | float | Lead score 0–100 (see breakdown below) |
| `segment` | str | `micro / small / medium / large` |

### Score breakdown

| Signal | Max pts | Thresholds |
|--------|---------|------------|
| Review count | 30 | ≥500→30, ≥200→24, ≥100→18, ≥50→12, ≥10→7, ≥1→3 |
| Star rating | 25 | ≥4.5→25, ≥4.0→20, ≥3.5→15, ≥3.0→10, >0→5 |
| Website presence | 30 | has_website+10, domain_valid+5, web_has_contact+5, web_has_services+5, web_is_modern+5 |
| Phone | 15 | has_phone→15 |

| Segment | Score range |
|---------|-------------|
| micro | 0–24 |
| small | 25–49 |
| medium | 50–74 |
| large | 75–100 |

---

## Architecture

```
mapScraper/
├── mapScraperX.py          original scraper CLI (unchanged)
├── main.py                 new pipeline CLI
├── requirements.txt
├── mapScraper/
│   └── placesCrawlerV2.py  async Google Maps scraper (deduplicates by id on save)
├── enrichment/
│   ├── features.py         feature engineering from CSV columns
│   ├── web_scraper.py      async website signal extraction
│   └── scoring.py          lead scoring (0–100) + segmentation
├── pipeline/
│   └── orchestrator.py     run_pipeline() — wires scrape & enrich
└── data/
    └── output.csv          scrape output (example)
```

### Design principles

- Scraper and enrichment are **fully independent** — enrichment never imports scraper logic and vice versa.
- Scraper output schema is **frozen** — the 13-column CSV is never modified.
- Enriched output is a **superset** of the raw CSV — every original column is preserved.
- Website scraping is **fault-tolerant** — any domain that fails returns empty signals without crashing the pipeline.
- Enrichment accepts **any previously generated CSV** as input — no need to re-scrape.
- Duplicates are removed by `id` at save time — first occurrence wins.

---

## Supported languages and countries

| Code | Language | Code | Country |
|------|----------|------|---------|
| `en` | English | `us` | United States |
| `es` | Spanish | `es` | Spain |
| `fr` | French | `fr` | France |
| `de` | German | `de` | Germany |
| `it` | Italian | `it` | Italy |
| `pt` | Portuguese | `br` | Brazil |
| `ja` | Japanese | `jp` | Japan |
| `ko` | Korean | `kr` | South Korea |
| `zh` | Chinese | `cn` | China |

---

## What changed (April 2026 fix)

Google shut down the `/localservices/prolist` endpoint (HTTP 410).

The scraper now uses a two-step approach:
1. `GET https://www.google.com/maps/search/{query}` — extracts a canonical `pb=` URL from the Maps SPA page.
2. `GET https://www.google.com/search?tbm=map&…&pb=…` — parses the `)]}'`-prefixed JSON at `data[64]`.

`requests-html` / pyppeteer removed; only `aiohttp` and `tqdm` needed for scraping.

---

## Troubleshooting

**Empty results / "Could not find pb= search URL"**
Google may be serving a consent wall. Try matching `--lang` and `--country` to your locale.

**"data[64] is missing"**
Google may have changed the response structure again. Run with `--log-level DEBUG` and open an issue.

**Enriched CSV has empty `web_*` columns**
The domain may be unreachable. Check `web_scraped` column — `False` means the fetch failed silently (expected behaviour). Use `--web-timeout 20` for slow sites.

**Large CSVs are slow to enrich**
Web scraping is the bottleneck. Increase `--web-concurrent 20` or skip it entirely with `--no-web-scraping`.

---

## License

Provided as-is for educational and research purposes. Please respect Google's Terms of Service.
