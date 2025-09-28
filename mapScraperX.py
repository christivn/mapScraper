import sys
import os
import argparse
import time
from tqdm import tqdm
import mapScraper.placesCrawlerV2 as crawler

def read_queries_from_file(file_path):
    """Read queries from a text file"""
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
    """Process a single query"""
    print(f"Processing query: '{query}'")
    results = crawler.search(query, lang, country, limit)
    print(f"Found {len(results)} results for '{query}'")
    return results

def process_multiple_queries(queries, lang, country, limit_per_query, max_concurrent=3):
    """Process multiple queries concurrently"""
    total_queries = len(queries)
    
    print(f"Processing {total_queries} queries concurrently (max {max_concurrent} at a time)...")
    
    start_time = time.time()
    
    # Use async search for multiple queries
    results = crawler.search_multiple(queries, lang, country, limit_per_query, max_concurrent)
    
    elapsed_time = time.time() - start_time
    
    print(f"\nCompleted in {elapsed_time:.2f} seconds")
    print(f"Average time per query: {elapsed_time/total_queries:.2f} seconds")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Google Maps for local services with concurrent processing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single query:
    python mapScraperX.py "restaurants in Miami" --limit 50
  
  Multiple queries (concurrent processing by default):
    python mapScraperX.py --queries-file query_example.txt
  
  Adjust concurrency level:
    python mapScraperX.py --queries-file query_example.txt --concurrent 5
        """
    )
    
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument('query', nargs='?', type=str, help='The search query.')
    query_group.add_argument('--queries-file', type=str, help='Path to a text file containing one query per line.')
    
    parser.add_argument('--lang', type=str, default='en', help='Language code (e.g., en, es, fr). Default: en')
    parser.add_argument('--country', type=str, default='us', help='Country code (e.g., us, es, fr). Default: us')
    parser.add_argument('--limit', type=int, help='Max results (total for single query, per query for file mode)')
    parser.add_argument('--output-file', type=str, default='data/output.csv', help='Output CSV file path. Default: data/output.csv')
    parser.add_argument('--concurrent', type=int, default=3, help='Max concurrent queries (default: 3, recommended: 3-5)')
    
    args = parser.parse_args()
    
    
    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    
    if args.query:
        print("Mode: Single query")
        results = process_single_query(args.query, args.lang, args.country, args.limit)
    
    elif args.queries_file:
        print(f"Mode: Multiple queries from file ({args.queries_file})")
        queries = read_queries_from_file(args.queries_file)
        
        if not queries:
            print("No valid queries found in the file.")
            sys.exit(1)
        
        print(f"Concurrent processing enabled: {args.concurrent} queries at a time")
        if args.limit:
            print(f"Limit per query: {args.limit}")
        
        results = process_multiple_queries(
            queries, 
            args.lang, 
            args.country, 
            args.limit,
            max_concurrent=args.concurrent
        )
    
    
    if results:
        crawler.save_to_csv(results, args.output_file)
        print(f"\n{'='*50}")
        print(f"Final Summary:")
        print(f"  Total results: {len(results)}")
        print(f"  File saved to: {args.output_file}")
        print(f"{'='*50}")
    else:
        print("No results found.")