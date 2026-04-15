![Header](https://github.com/christivn/mapScraper/blob/main/github-header-image.png?raw=true)

#### Contributors

<a href="https://github.com/christivn/mapScraper/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=christivn/mapScraper" />
</a>

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
   pip install requests-html lxml[html_clean] urllib3 phonenumbers
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

This project is provided as-is for educational and research purposes. Please respect Google's Terms of Service and use responsibly.


