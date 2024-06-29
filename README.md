# 🤖🗺️ Google Maps Scraper

Headless browser scraper written in python to extract data from Google Maps Places.

**Required packages:**
- requests_html
- urllib
- json
<br><br>

## ➡️ Example code
``` python
from mapScraper import placesCrawler

query = "Gym in Seville Spain"
results = placesCrawler.search(query)

print(results)
```

**Example output:**
``` json
[
  {
    "id": "ChIJP0UWUA9sEg0RuJoxZuLavLs",
    "title": "Sevilla",
    "category": "Gym",
    "address": "C. Amor de Dios, 35, Casco Antiguo, 41002 Sevilla",
    "phoneNumber": "681 96 61 09",
    "completePhoneNumber": "+34 681 96 61 09",
    "domain": "instagram.com",
    "url": "https://instagram.com/sevillagym_oficial?utm_medium=copy_link",
    "coor": "37.3958503,-5.994440399999999",
    "stars": 4.3,
    "reviews": 253
  },
  {
    "id": "ChIJD6RGzE9pEg0RJmWVq_nh2j0",
    "title": "Sevilla Century Fitness Gym",
    "category": "Gymnastics center",
    "address": "Av. del Alcalde Manuel del Valle, 50, Norte, 41015 Sevilla",
    "phoneNumber": "691 84 08 73",
    "completePhoneNumber": "+34 691 84 08 73",
    "domain": "www.centuryfitness.es",
    "url": "https://www.centuryfitness.es/",
    "coor": "37.4127951,-5.9724556",
    "stars": 4.8,
    "reviews": 2442
  },
  # ... (other entries are similar)
  {
    "id": "ChIJNYda7WtsEg0RCC83FLkQK1Q",
    "title": "Hispanic Happiness Club",
    "category": "Athletic club",
    "address": "C. Ignacio Gómez Millán, s/n, 41010 Sevilla",
    "phoneNumber": "954 33 88 08",
    "completePhoneNumber": "+34 954 33 88 08",
    "domain": "www.galisport.com",
    "url": "http://www.galisport.com/",
    "coor": "37.3839533,-6.007852499999999",
    "stars": 3.5,
    "reviews": 172
  }
]
```
