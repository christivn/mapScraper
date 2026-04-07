![Header](https://github.com/christivn/mapScraper/blob/main/github-header-image.png?raw=true)

# Google Maps Scraper

A powerful Python tool for scraping Google Maps local services data. Extract detailed information about businesses and places directly from Google Maps search results.

## 🚀 Features

With the **Google Maps Scraper**, you can obtain detailed data about businesses and specific places on Google Maps, such as:

- **Place ID** - Unique identifier for the location
- **Place URL** - Direct Google Maps link
- **Place name** - Business or location name
- **Category** - Type of business/service
- **Full address** - Complete location address
- **Phone number** - Contact phone number
- **Associated domain and URL** - Business website information
- **Coordinates** - Latitude and longitude
- **Average star rating** - Customer rating
- **Number of reviews** - Total review count
- **Customizable search parameters** - Language, country, result limit, and output filename

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/christivn/mapScraper.git
   cd mapScraper
   ```

2. **Install required packages:**
   ```bash
   pip install aiohttp tqdm
   ```

3. **Verify installation:**
   ```bash
   python mapScraperX.py --help
   ```

## 🔧 Usage

### Basic Syntax
```bash
python mapScraperX.py "your search query" [options]
```

### Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `query` | Search query (required) | - | `"restaurants in NYC"` |
| `--lang` | Language code | `en` | `--lang es` |
| `--country` | Country code | `us` | `--country fr` |
| `--limit` | Maximum results | No limit | `--limit 100` |
| `--output-file` | Output CSV file path | `data/output.csv` | `--output-file results.csv` |

### 💡 Usage Examples

#### Basic Search
```bash
# Search for gyms in Seville, Spain
python mapScraperX.py "Gym in Seville Spain"
```

#### Language and Country Specific Search
```bash
# Search for dentists in Madrid (Spanish language, Spain country)
python mapScraperX.py "dentistas en Madrid" --lang es --country es
```

#### Limited Results
```bash
# Get only 50 pizza places in Paris
python mapScraperX.py "pizzerias in Paris" --lang fr --country fr --limit 50
```

#### Custom Output File
```bash
# Save results to a custom file
python mapScraperX.py "coffee shops in London" --output-file "data/london_coffee.csv"
```

#### Complex Query with All Options
```bash
# Comprehensive search with all parameters
python mapScraperX.py "barber shops in Tokyo" --lang ja --country jp --limit 25 --output-file "data/tokyo_barbers.csv"
```
### Complex query using file (for multiple queries)
```bash
# Comprehensive search using query list
python mapScraperX.py --queries-file qwuery_example.txt --lang ja --country jp --limit 25 --output-file "data/custom_name.csv"
```

### Concurrent query processing
```bash
# When requesting for more than one query (safe):
python mapScraperX.py --queries-file qwuery_example.txt --lang en --country jp --limit 25 --output-file "data/custom_name.csv" --concurrent 2
```

```bash
# When requesting for more than one query (fast but risky):
python mapScraperX.py --queries-file qwuery_example.txt --lang en --country jp --limit 25 --output-file "data/custom_name.csv" --concurrent 5
```


## 🌍 Supported Languages and Countries

### Common Language Codes
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese

### Common Country Codes
- `us` - United States
- `gb` - United Kingdom
- `es` - Spain
- `fr` - France
- `de` - Germany
- `it` - Italy
- `jp` - Japan
- `ca` - Canada
- `au` - Australia

## 📁 Output Format

The scraper generates a CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Google Place ID | `ChIJN1t_tDeuEmsRUsoyG83frY4` |
| `url_place` | Direct Google Maps link | `https://www.google.com/maps/place/?q=place_id:...` |
| `title` | Business name | `Joe's Pizza` |
| `category` | Business category | `Pizza restaurant` |
| `address` | Full address | `123 Main St, New York, NY 10001` |
| `phoneNumber` | Local phone format | `(555) 123-4567` |
| `completePhoneNumber` | International format | `+1 555-123-4567` |
| `domain` | Website domain | `joespizza.com` |
| `url` | Full website URL | `https://www.joespizza.com` |
| `coor` | Coordinates (lat,lng) | `40.7128,-74.0060` |
| `stars` | Average rating | `4.5` |
| `reviews` | Number of reviews | `234` |

## 🔧 What Changed (April 2026 Fix)

Google permanently shut down the `/localservices/prolist` endpoint that this
scraper originally used (it now returns **HTTP 410 Gone**).

**What was changed:**
- The scraper no longer targets `/localservices/prolist`. It now uses a
  two-step approach:
  1. `GET https://www.google.com/maps/search/{query}` — fetches the Maps SPA
     page to extract an embedded canonical `pb=` search URL from the `<link>`
     tag in `<head>`.
  2. `GET https://www.google.com/search?tbm=map&...&pb=...` — fetches a
     `)]}'`-prefixed JSON payload that contains the actual search results in a
     nested array at `data[64]`.
- JavaScript rendering via `requests-html` / pyppeteer is **no longer needed**.
  Both requests are plain HTTP GETs; this makes the scraper faster and removes
  a heavyweight dependency.
- `requests-html` has been removed from `requirements.txt`. Only `aiohttp` and
  `tqdm` are required now.
- All extraction failures now log explicit error messages so failures are never
  silent.

**Known limitation:** The `tbm=map` JSON response does not include review
counts. The `reviews` column in the output CSV will be empty. All other fields
(id, title, category, address, phone, website, coordinates, stars) are fully
populated.

## 📦 Installation (Updated)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/christivn/mapScraper.git
   cd mapScraper
   ```

2. **Install required packages:**
   ```bash
   pip install aiohttp tqdm
   ```

3. **Verify installation:**
   ```bash
   python mapScraperX.py --help
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Empty results / "Could not find pb= search URL"**
   - Google may be showing a consent or cookie wall for your IP/region.
   - Try setting `--lang` and `--country` to match your actual locale.
   - Check your internet connection.

2. **"data[64] is missing"**
   - Google may have updated the response structure again.
   - Open an issue with the raw response logged at DEBUG level:
     ```bash
     python -c "import logging; logging.basicConfig(level=logging.DEBUG); \
       import mapScraper.placesCrawlerV2 as c; c.search('test', 'en', 'us', 5)"
     ```

3. **Permission denied when creating output directory**
   - Ensure you have write permissions in the target directory.
   - Try running with appropriate permissions or change the output path.

## 📝 License

This project is provided as-is for educational and research purposes. Please respect Google's Terms of Service and use responsibly.


