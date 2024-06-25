from src import placesCrawler
import json

query = "Gimnasio en Sevilla España"
results = placesCrawler.search(query)

print(json.loads(results))
