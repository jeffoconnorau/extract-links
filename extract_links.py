import sys
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_page_details(url):
    """Fetches the page title and last modified date."""
    title = "Unknown"
    last_modified = ""
    try:
        # We use a short timeout because there could be many links
        response = requests.get(url, timeout=5, verify=False)
        # Check Last-Modified header
        if 'Last-Modified' in response.headers:
            last_modified = response.headers['Last-Modified']
            
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
    except Exception as e:
        title = f"Error fetching"
        
    return title, last_modified

def extract_links_to_file(source_url, output_filename="extracted_links.txt", fetch_all=False, export_csv=False, include_anchors=False, recursive=True):
    unique_urls = set()
    urls_to_visit = [source_url]
    visited_urls = set()
    base_url_prefix = None

    # Common extensions to skip when crawling
    skip_extensions = ('.pdf', '.png', '.jpg', '.jpeg', '.gif', '.zip', '.tar', '.gz', '.csv', '.json', '.xml', '.css', '.js')

    try:
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited_urls:
                continue
                
            visited_urls.add(current_url)
            
            try:
                # Show queue size if recursive is on
                queue_info = f" (Queue: {len(urls_to_visit)})" if recursive else ""
                print(f"Fetching {current_url}...{queue_info}")
                
                response = requests.get(current_url, verify=False, timeout=10)
                
                # Check that we received actual HTML before parsing
                content_type = response.headers.get('Content-Type', "")
                if 'text/html' not in content_type:
                    continue
                    
                resolved_url = response.url
                
                # Initialize the base prefix boundary from the first sourceURL resolved
                if base_url_prefix is None:
                    parsed_source = urlparse(resolved_url)
                    base_path = parsed_source.path
                    if not base_path.endswith('/'):
                        if '.' in base_path.split('/')[-1]:
                            base_path = base_path.rsplit('/', 1)[0] + '/'
                        else:
                            base_path = base_path + '/'
                    base_url_prefix = f"{parsed_source.scheme}://{parsed_source.netloc}{base_path}"
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for link in soup.find_all('a'):
                    href = link.get('href')
                    if not href:
                        continue
                        
                    # Convert relative URLs to absolute URLs
                    full_url = urljoin(resolved_url, href)
                    
                    # Ensure it's a web link
                    if full_url.startswith(('http://', 'https://')):
                        if not include_anchors:
                            parsed_url = urlparse(full_url)
                            if parsed_url.fragment:
                                full_url = parsed_url._replace(fragment="").geturl()

                        is_within_base = full_url.startswith(base_url_prefix)
                        
                        if fetch_all or is_within_base:
                            unique_urls.add(full_url)
                            
                            # Add to visit queue if we are recursive and it's within docs boundaries
                            if recursive and is_within_base:
                                if full_url not in visited_urls and full_url not in urls_to_visit:
                                    if not full_url.lower().endswith(skip_extensions):
                                        urls_to_visit.append(full_url)
                                        
            except Exception as e:
                print(f"  Failed to process {current_url}: {e}")

        sorted_urls = sorted(unique_urls)
        print(f"\nSuccessfully extracted {len(sorted_urls)} unique URLs across {len(visited_urls)} parsed pages.")
        if not fetch_all:
             print(f"(Filtered to only include links within {base_url_prefix})")
             
        if export_csv:
            print(f"Fetching details for {len(sorted_urls)} links. This may take a moment...")
            
            with open(output_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "URL", "Last Modified"])
                
                for idx, url in enumerate(sorted_urls, start=1):
                    # Print progress on the same line
                    print(f"\rProcessing {idx}/{len(sorted_urls)}: {url[:50]}...", end="", flush=True)
                    title, last_modified = fetch_page_details(url)
                    writer.writerow([idx, title, url, last_modified])
            print("\nCSV extraction complete.")
        else:
            # Write the unique URLs to the output text file
            with open(output_filename, 'w', encoding='utf-8') as f:
                for url in sorted_urls:
                    f.write(url + '\n')
                    
        print(f"Saved to: {output_filename}")

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Saved data from the pages processed so far.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract hyperlinks from a webpage and save them to a file.", add_help=False)
    
    parser.add_argument("--url", "--u", required=True, help="The source URL to extract links from")
    parser.add_argument("--all", "--a", action="store_true", help="Extract all HTTP/HTTPS links, not just those in the same directory")
    parser.add_argument("--csv", "--c", action="store_true", help="Export to a CSV file containing link ID, page title, URL, and last modified date")
    parser.add_argument("--anchor", "--an", action="store_true", help="Include URLs with anchor fragments (e.g., #section)")
    parser.add_argument("--no-recursive", "--nr", action="store_false", dest="recursive", help="Do not recursively crawl subfolders (crawling is enabled by default)")
    parser.add_argument("--output", "--o", default="extracted_links.txt", help="Output filename (default: extracted_links.txt)")
    parser.add_argument("--help", "--h", action="help", default=argparse.SUPPRESS, help="Show this help message and exit")
    
    args = parser.parse_args()
    
    extract_links_to_file(args.url, output_filename=args.output, fetch_all=args.all, export_csv=args.csv, include_anchors=args.anchor, recursive=args.recursive)
