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
   pip install requests-html lxml[html_clean] urllib3
   ```

   > **Note:** If you encounter issues with `lxml`, try installing it separately:
   > ```bash
   > pip install lxml[html_clean]
   > ```

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

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'requests_html'"**
   ```bash
   pip install requests-html
   ```

2. **lxml installation errors**
   ```bash
   pip install lxml[html_clean]
   # or on some systems:
   pip install --upgrade lxml
   ```

3. **Permission denied when creating output directory**
   - Ensure you have write permissions in the target directory
   - Try running with appropriate permissions or change the output path

4. **Empty results**
   - Check your internet connection
   - Verify the search query is valid
   - Try different language/country combinations

## 📝 License

This project is provided as-is for educational and research purposes. Please respect Google's Terms of Service and use responsibly.


