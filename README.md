# 🤖🗺️ Google Maps Scraper

Headless browser scraper written in python to extract Places data from Google Maps, compatible with rotating proxies.

**Required packages:**
- 1
- 2
- 3
<br><br>

## ⚡ How to install
**1.** Clone this repository inside your project:

``git clone https://github.com/christivn/Google-Places-Scraper.git``

<br><br><br>

## ➡️ Example code
``` python
from src import placesCrawler

query = "Gimnasio en Sevilla España"
results = placesCrawler.search(query)

print(results)
```

Example individual output:
``` json
{
  "title": "OKEYMAS Fitness Club",
  "category": "Fitness center",
  "address": "Pl. Ximénez de Sandoval, 2, 41710 Utrera, Sevilla", 
  "website": "https://okeymas.es/utrera",
  "phoneNumber": "744618706",
  "rating": 4.6,
  "ratingCount": 130
}
```
