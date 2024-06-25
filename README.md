# 🤖🗺️ Google Maps Scraper

Headless browser scraper written in python to extract Places data from Google Maps.

**Required packages:**
- requests_html
- urllib
<br><br>

## ⚡ How to install
**1.** Clone this repository inside your project:

``git clone https://github.com/christivn/Google-Places-Scraper.git``

<br><br>

## ➡️ Example code
``` python
from src import placesCrawler

query = "Gimnasio en Sevilla España"
results = placesCrawler.search(query)

print(results)
```

**Example output:**
``` json
{
  "title": "OKEYMAS Fitness Club",
  "category": "Fitness center",
  "address": "Pl. Ximénez de Sandoval, 2, 41710 Utrera, Sevilla", 
  "website": "https://okeymas.es/utrera",
  "phoneNumber": "744618706",
  "rating": 4.6,
  "ratingCount": 130
},
{
  "title": "Planet Gym Bormujos", 
  "category": "Gym", 
  "address": "Av Juan Carlos Rey de España nº 55 local, 41930 Bormujos, Sevilla", 
  "website": "https://planetgymsport.es/bormujos/", 
  "phoneNumber": "955528389", 
  "rating": 4.5, 
  "ratingCount": 149
},
...
..
.
```
