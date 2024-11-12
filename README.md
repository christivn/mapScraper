# 🤖🗺️ mapScraper

This project is a **Python-based web scraper** that uses a headless browser to extract information about places from Google Maps.

<br>

## 🚀 Features
With the **Google Maps Scraper**, you can obtain detailed data about businesses and specific places on Google Maps, such as:
- Place ID
- Place name
- Category
- Full address
- Phone number
- Associated domain and URL
- Coordinates (latitude and longitude)
- Average star rating
- Number of reviews

<br>

## 📦 Required Packages
To run this scraper, you'll need the following Python packages:
- `requests_html` - for making HTML requests and rendering dynamic content
- `urllib` - for URL handling
- `json` - for managing structured data in JSON format

<br>

## ➡️ Code Example
Here's a basic usage example:

```python
from mapScraper import placesCrawlerV2

# Define your query
query = "Gym in Seville Spain"
# Run the search
results = placesCrawlerV2.search(query)

# Display the results
print(results)
```

<br>

## 📋 Example Output
The scraper returns a list in JSON format with detailed information about the found places. Here’s a sample output:

```json
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

<br>

## 🛠️ Setup and Usage
1. Clone this repository.
2. Make sure you have the necessary packages installed.
3. Modify the `query` to customize your search and run the script to see the results.

<br>

## ⚠️ Note
This project is for educational and research purposes only. Please respect Google’s usage policies and terms of service.
