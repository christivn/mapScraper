import sys
import os
import argparse
import time
from tqdm import tqdm
import mapScraper.placesCrawlerV2 as crawler

def read_queries_from_file(file_path):
    queries = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                query = line.strip()
                if query and not query.startswith('#'):
                    queries.append(query)
        return queries
    except FileNotFoundError:
        print(f"Error: Could not find the file {file_path}")
        return []
    except Exception as e:
        print(f"Error reading the file {file_path}: {e}")
        return []

def process_single_query(query, lang, country, limit):
    print(f"Processing query: '{query}'")
    results = crawler.search(query, lang, country, limit)
    print(f"Found {len(results)} results for '{query}'")
    return results

def process_multiple_queries(queries, lang, country, limit_per_query):
    all_results = []
    total_queries = len(queries)
    
    progress_bar = tqdm(queries, desc="Processing queries", unit="query")
    
    for i, query in enumerate(progress_bar, 1):
        progress_bar.set_description(f"Query {i}/{total_queries}: {query[:30]}{'...' if len(query) > 30 else ''}")
        
        try:
            results = crawler.search(query, lang, country, limit_per_query)
            
            for result in results:
                result['source_query'] = query
            
            all_results.extend(results)
            
            progress_bar.set_postfix({
                'Found': len(results),
                'Total accumulated': len(all_results)
            })
            
            time.sleep(0.5)
            
        except Exception as e:
            progress_bar.set_postfix({
                'Error': str(e)[:20] + '...' if len(str(e)) > 20 else str(e)
            })
            time.sleep(1)
            continue
    
    progress_bar.close()
    return all_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Google Maps for local services.")
    
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument('query', nargs='?', type=str, help='The search query.')
    query_group.add_argument('--queries-file', type=str, help='Path to a text file containing one query per line.')
    
    parser.add_argument('--lang', type=str, default='en', help='The language for the search (e.g., en, es, fr). Default is "en".')
    parser.add_argument('--country', type=str, default='us', help='The country for the search (e.g., us, es, fr). Default is "us".')
    parser.add_argument('--limit', type=int, help='The maximum number of results to retrieve (total for single query, per query for file mode).')
    parser.add_argument('--output-file', type=str, default='data/output.csv', help='The output CSV file path. Default is "data/output.csv".')
    
    args = parser.parse_args()
    
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if args.query:
        print("Mode: Single query")
        results = process_single_query(args.query, args.lang, args.country, args.limit)
    
    elif args.queries_file:
        print(f"Mode: Queries file ({args.queries_file})")
        queries = read_queries_from_file(args.queries_file)
        
        if not queries:
            print("No valid queries found in the file.")
            sys.exit(1)
        
        print(f"Processing {len(queries)} queries")
        if args.limit:
            print(f"Limit per query: {args.limit}")
        
        results = process_multiple_queries(queries, args.lang, args.country, args.limit)
    
    if results:
        crawler.save_to_csv(results, args.output_file)
        print(f"\nFinal Summary:")
        print(f"Total results: {len(results)}")
        print(f"File saved to: {args.output_file}")
    else:
        print("No results found.")