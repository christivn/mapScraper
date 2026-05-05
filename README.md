![Header](https://github.com/christivn/mapScraper/blob/main/github-header-image.png?raw=true)

# 🗺️🤖 mapScraper - Google Maps Scraper

A Python tool for scraping Google Maps local services data **and** enriching the results with lead-scoring signals.

### Contributors

<a href="https://github.com/christivn/mapScraper/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=christivn/mapScraper" />
</a>

## 🚀 Features

| Script | Purpose |
|--------|---------|
| `mapScraperX.py` | Original scraper CLI — unchanged, backward-compatible |
| `main.py` | New pipeline CLI with `scrape / enrich / full` modes |

- **Place ID** - Unique identifier for the location
- **Place URL** - Direct Google Maps link
- **Place name** - Business or location name
- **Category** - Type of business/service
- **Full address** - Complete location address
- **Phone number** - Contact phone number
- **Associated domain and URL** - Business website information
- **Average star rating** - Customer rating
- **Number of reviews** - Total review count
- **Customizable search parameters** - Language, country, result limit, and output filename

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

2. **Install required packages:**
   ```bash
   pip install requests-html lxml[html_clean] urllib3 phonenumbers
   ```

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

The `--lang` flag maps to Google's `hl` parameter (interface language) and `--country` maps to `gl` (geolocation). Both are case-insensitive.

### Language Codes (`--lang` / `hl`)

| Code | Language | Code | Language | Code | Language |
|------|----------|------|----------|------|----------|
| `af` | Afrikaans | `ga` | Irish | `pa` | Punjabi |
| `ak` | Akan | `gl` | Galician | `qu` | Quechua |
| `sq` | Albanian | `ka` | Georgian | `ro` | Romanian |
| `am` | Amharic | `de` | German | `rm` | Romansh |
| `ar` | Arabic | `el` | Greek | `ru` | Russian |
| `hy` | Armenian | `kl` | Greenlandic | `gd` | Scots Gaelic |
| `az` | Azerbaijani | `gn` | Guarani | `sr` | Serbian |
| `eu` | Basque | `gu` | Gujarati | `sh` | Serbo-Croatian |
| `be` | Belarusian | `ht` | Haitian Creole | `st` | Sesotho |
| `bem` | Bemba | `ha` | Hausa | `tn` | Setswana |
| `bn` | Bengali | `haw` | Hawaiian | `sn` | Shona |
| `bh` | Bihari | `he` | Hebrew | `sd` | Sindhi |
| `bs` | Bosnian | `hi` | Hindi | `si` | Sinhalese |
| `br` | Breton | `hu` | Hungarian | `sk` | Slovak |
| `bg` | Bulgarian | `is` | Icelandic | `sl` | Slovenian |
| `km` | Cambodian | `ig` | Igbo | `so` | Somali |
| `ca` | Catalan | `id` | Indonesian | `es` | Spanish |
| `chr` | Cherokee | `ia` | Interlingua | `es-419` | Spanish (Latin American) |
| `ny` | Chichewa | `it` | Italian | `su` | Sundanese |
| `zh-cn` | Chinese (Simplified) | `ja` | Japanese | `sw` | Swahili |
| `zh-tw` | Chinese (Traditional) | `jw` | Javanese | `sv` | Swedish |
| `co` | Corsican | `kn` | Kannada | `tg` | Tajik |
| `hr` | Croatian | `kk` | Kazakh | `ta` | Tamil |
| `cs` | Czech | `rw` | Kinyarwanda | `tt` | Tatar |
| `da` | Danish | `rn` | Kirundi | `te` | Telugu |
| `nl` | Dutch | `ko` | Korean | `th` | Thai |
| `en` | English | `ku` | Kurdish | `ti` | Tigrinya |
| `eo` | Esperanto | `ckb` | Kurdish (Sorani) | `to` | Tonga |
| `et` | Estonian | `ky` | Kyrgyz | `tr` | Turkish |
| `ee` | Ewe | `lo` | Laothian | `tk` | Turkmen |
| `fo` | Faroese | `la` | Latin | `uk` | Ukrainian |
| `tl` | Filipino | `lv` | Latvian | `ur` | Urdu |
| `fi` | Finnish | `ln` | Lingala | `uz` | Uzbek |
| `fr` | French | `lt` | Lithuanian | `vi` | Vietnamese |
| `fy` | Frisian | `lg` | Luganda | `cy` | Welsh |
| `gaa` | Ga | `mk` | Macedonian | `wo` | Wolof |
| | | `mg` | Malagasy | `xh` | Xhosa |
| | | `ms` | Malay | `yi` | Yiddish |
| | | `ml` | Malayalam | `yo` | Yoruba |
| | | `mt` | Maltese | `zu` | Zulu |
| | | `mi` | Maori | | |
| | | `mr` | Marathi | | |
| | | `mn` | Mongolian | | |
| | | `my` | Myanmar (Burmese) | | |
| | | `ne` | Nepali | | |
| | | `no` | Norwegian | | |
| | | `nn` | Norwegian (Nynorsk) | | |
| | | `oc` | Occitan | | |
| | | `or` | Oriya | | |
| | | `om` | Oromo | | |
| | | `ps` | Pashto | | |
| | | `fa` | Persian | | |
| | | `pl` | Polish | | |
| | | `pt` | Portuguese | | |
| | | `pt-br` | Portuguese (Brazil) | | |
| | | `pt-pt` | Portuguese (Portugal) | | |

### Country Codes (`--country` / `gl`)

| Code | Country | Code | Country | Code | Country |
|------|---------|------|---------|------|---------|
| `af` | Afghanistan | `ge` | Georgia | `ni` | Nicaragua |
| `al` | Albania | `de` | Germany | `ne` | Niger |
| `dz` | Algeria | `gh` | Ghana | `ng` | Nigeria |
| `as` | American Samoa | `gi` | Gibraltar | `no` | Norway |
| `ad` | Andorra | `gr` | Greece | `om` | Oman |
| `ao` | Angola | `gl` | Greenland | `pk` | Pakistan |
| `ai` | Anguilla | `gd` | Grenada | `pw` | Palau |
| `ag` | Antigua and Barbuda | `gp` | Guadeloupe | `ps` | Palestinian Territory |
| `ar` | Argentina | `gu` | Guam | `pa` | Panama |
| `am` | Armenia | `gt` | Guatemala | `pg` | Papua New Guinea |
| `aw` | Aruba | `gg` | Guernsey | `py` | Paraguay |
| `au` | Australia | `gn` | Guinea | `pe` | Peru |
| `at` | Austria | `gw` | Guinea-Bissau | `ph` | Philippines |
| `az` | Azerbaijan | `gy` | Guyana | `pn` | Pitcairn |
| `bs` | Bahamas | `ht` | Haiti | `pl` | Poland |
| `bh` | Bahrain | `va` | Vatican City | `pt` | Portugal |
| `bd` | Bangladesh | `hn` | Honduras | `pr` | Puerto Rico |
| `bb` | Barbados | `hk` | Hong Kong | `qa` | Qatar |
| `by` | Belarus | `hu` | Hungary | `re` | Reunion |
| `be` | Belgium | `is` | Iceland | `ro` | Romania |
| `bz` | Belize | `in` | India | `ru` | Russian Federation |
| `bj` | Benin | `id` | Indonesia | `rw` | Rwanda |
| `bm` | Bermuda | `ir` | Iran | `sh` | Saint Helena |
| `bt` | Bhutan | `iq` | Iraq | `kn` | Saint Kitts and Nevis |
| `bo` | Bolivia | `ie` | Ireland | `lc` | Saint Lucia |
| `ba` | Bosnia and Herzegovina | `im` | Isle of Man | `pm` | Saint Pierre and Miquelon |
| `bw` | Botswana | `il` | Israel | `vc` | Saint Vincent and the Grenadines |
| `br` | Brazil | `it` | Italy | `ws` | Samoa |
| `bn` | Brunei | `jm` | Jamaica | `sm` | San Marino |
| `bg` | Bulgaria | `jp` | Japan | `st` | Sao Tome and Principe |
| `bf` | Burkina Faso | `je` | Jersey | `sa` | Saudi Arabia |
| `bi` | Burundi | `jo` | Jordan | `sn` | Senegal |
| `kh` | Cambodia | `kz` | Kazakhstan | `rs` | Serbia |
| `cm` | Cameroon | `ke` | Kenya | `sc` | Seychelles |
| `ca` | Canada | `ki` | Kiribati | `sl` | Sierra Leone |
| `cv` | Cape Verde | `kp` | North Korea | `sg` | Singapore |
| `ky` | Cayman Islands | `kr` | South Korea | `sk` | Slovakia |
| `cf` | Central African Republic | `kw` | Kuwait | `si` | Slovenia |
| `td` | Chad | `kg` | Kyrgyzstan | `sb` | Solomon Islands |
| `cl` | Chile | `la` | Laos | `so` | Somalia |
| `cn` | China | `lv` | Latvia | `za` | South Africa |
| `co` | Colombia | `lb` | Lebanon | `es` | Spain |
| `km` | Comoros | `ls` | Lesotho | `lk` | Sri Lanka |
| `cg` | Congo | `lr` | Liberia | `sd` | Sudan |
| `cd` | Congo (DRC) | `ly` | Libya | `sr` | Suriname |
| `ck` | Cook Islands | `li` | Liechtenstein | `sz` | Eswatini |
| `cr` | Costa Rica | `lt` | Lithuania | `se` | Sweden |
| `ci` | Cote D'Ivoire | `lu` | Luxembourg | `ch` | Switzerland |
| `hr` | Croatia | `mo` | Macao | `sy` | Syria |
| `cu` | Cuba | `mk` | North Macedonia | `tw` | Taiwan |
| `cy` | Cyprus | `mg` | Madagascar | `tj` | Tajikistan |
| `cz` | Czech Republic | `mw` | Malawi | `tz` | Tanzania |
| `dk` | Denmark | `my` | Malaysia | `th` | Thailand |
| `dj` | Djibouti | `mv` | Maldives | `tl` | Timor-Leste |
| `dm` | Dominica | `ml` | Mali | `tg` | Togo |
| `do` | Dominican Republic | `mt` | Malta | `tk` | Tokelau |
| `ec` | Ecuador | `mh` | Marshall Islands | `to` | Tonga |
| `eg` | Egypt | `mq` | Martinique | `tt` | Trinidad and Tobago |
| `sv` | El Salvador | `mr` | Mauritania | `tn` | Tunisia |
| `gq` | Equatorial Guinea | `mu` | Mauritius | `tr` | Turkey |
| `er` | Eritrea | `yt` | Mayotte | `tm` | Turkmenistan |
| `ee` | Estonia | `mx` | Mexico | `tc` | Turks and Caicos Islands |
| `et` | Ethiopia | `fm` | Micronesia | `tv` | Tuvalu |
| `fk` | Falkland Islands | `md` | Moldova | `ug` | Uganda |
| `fo` | Faroe Islands | `mc` | Monaco | `ua` | Ukraine |
| `fj` | Fiji | `mn` | Mongolia | `ae` | United Arab Emirates |
| `fi` | Finland | `me` | Montenegro | `gb` | United Kingdom |
| `fr` | France | `ms` | Montserrat | `us` | United States |
| `gf` | French Guiana | `ma` | Morocco | `uy` | Uruguay |
| `pf` | French Polynesia | `mz` | Mozambique | `uz` | Uzbekistan |
| `ga` | Gabon | `mm` | Myanmar | `vu` | Vanuatu |
| `gm` | Gambia | `na` | Namibia | `ve` | Venezuela |
| | | `nr` | Nauru | `vn` | Vietnam |
| | | `np` | Nepal | `vg` | Virgin Islands (British) |
| | | `nl` | Netherlands | `vi` | Virgin Islands (U.S.) |
| | | `nc` | New Caledonia | `wf` | Wallis and Futuna |
| | | `nz` | New Zealand | `ye` | Yemen |
| | | | | `zm` | Zambia |
| | | | | `zw` | Zimbabwe |

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

## 🔄 Implementation Details

The scraper has been refactored to use the Google Places search URL instead of the local services listing, which is no longer available. 

### How it works:

Search results are fetched directly from Google's Places tab:
`https://www.google.com/search?q={query}&start={pagination}&udm=1&hl={lang}&gl={country}`

- The `udm=1` parameter opens the places tab in Google results directly.
- The returned data is backed into HTML and scraped using reliable class names, IDs, and other patterns.
- For results without phone numbers, a separate asynchronous call is made to `https://www.google.com/async/lcl_akp?q={query}&async=ludocids:{cid},_fmt:prog` using the location's `cid` to fetch missing phone numbers, complete addresses, and website links.
- Fully asynchronous execution for maximum performance and efficiency.
- **Three scraping modes** for different use cases:
  - `fast`: Quick results without phone fallback
  - `standard`: Balanced with phone fallback (default)
  - `complete`: Thorough results with phone and address fallback

## 📝 License

---

## License

Provided as-is for educational and research purposes. Please respect Google's Terms of Service.
