import sys
import os
import argparse
import mapScraper.placesCrawlerV2 as crawler

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Google Maps for local services.")
    parser.add_argument('query', type=str, help='The search query.')
    parser.add_argument('--lang', type=str, default='en', help='The language for the search (e.g., en, es, fr). Default is "en".')
    parser.add_argument('--country', type=str, default='us', help='The country for the search (e.g., us, es, fr). Default is "us".')
    parser.add_argument('--limit', type=int, help='The maximum number of results to retrieve.')
    parser.add_argument('--output-file', type=str, default='data/output.csv', help='The output CSV file path. Default is "data/output.csv".')
    
    args = parser.parse_args()
    
    if not os.path.exists(os.path.dirname(args.output_file)):
        os.makedirs(os.path.dirname(args.output_file))

    results = crawler.search(args.query, args.lang, args.country, args.limit)
    crawler.save_to_csv(results, args.output_file)