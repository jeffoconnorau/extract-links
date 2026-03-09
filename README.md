# Link Extractor for help with explicit URL inference for AI bots or AI agents.

A simple Python script to extract and deduplicate hyperlinks from any given webpage. 

This tool is especially useful for feeding a list of URLs to an AI chatbot (like Gemini or ChatGPT) so it can browse and inference data across a specific topic or documentation site.

## Installation

This script requires Python 3 and two external libraries (`requests` and `beautifulsoup4`).

You can install the dependencies using pip:
```bash
python3 -m pip install requests beautifulsoup4
```

## Usage

Run the script from your terminal and provide the target URL. **By default, it acts as a Web Crawler**, fetching the given page *and* recursively crawling any subdirectories it finds to extract every possible link from that section of the site.

```bash
python3 extract_links.py --url https://example.com/docs/
```

### Options

The script supports the following command-line arguments (and their shortcuts):

*   `--url`, `--u`: **(Required)** The source URL to extract links from.
*   `--all`, `--a`: *(Optional)* Extract **all** HTTP/HTTPS links found on the page, rather than just those matching the source path.
*   `--csv`, `--c`: *(Optional)* Instead of a simple text list, fetch metadata for each link (Page Title & Last Modified date) and export as a CSV table format.
*   `--no-recursive`, `--nr`: *(Optional)* Disable **Web Crawler Mode**. By default, this script will crawl and fetch all pages it finds in the same directory (or subdirectories) to ensure it extracts every possible link from the entire site section! Use this flag to only extract links from the single provided URL.
*   `--anchor`, `--an`: *(Optional)* Include URLs with anchor fragments (e.g., `#section`). By default, anchors are removed to reduce duplicates.
*   `--output`, `--o`: *(Optional)* Define a custom output filename. (Defaults to `extracted_links.txt`).
*   `--help`, `--h`: *(Optional)* Show the help message and exit.

### Examples

**1. Basic Usage (Filter to path):**
This will extract links like `https://example.com/blog/post-1` but ignore links like `https://google.com` or `https://example.com/about`.
```bash
python3 extract_links.py --u https://example.com/blog/
```

**2. CSV Export with Metadata:**
This will fetch the title and edit date for each link found from the current directory, and format the output as `extracted_links.csv`.
```bash
python3 extract_links.py --u https://example.com/blog/ --csv
```

**3. Extract all URLs from a page:**
This will grab every valid `http://` or `https://` link on the page, regardless of where they point to.
```bash
python3 extract_links.py --u https://example.com/ --a
```

**4. Save to a custom file:**
```bash
python3 extract_links.py --u https://example.com/ --o my_custom_links.txt
```

## Output

Based on your options, the script generates either a plain text file or a CSV file.

### Text Output (Default)
Generates a file where:
*   Every URL is on its own line.
*   All relative URLs (e.g., `/contact`) are automatically converted to absolute URLs (e.g., `https://example.com/contact`).
*   The list is automatically deduplicated and alphabetically sorted.

### CSV Output (Using `--csv`)
Generates a `.csv` file format containing 4 columns:
*   `ID`: The numeric rank counting the extracted urls (starts from 1).
*   `Title`: The extracted `<title>` from the HTML page of that specific link.
*   `URL`: The absolute URL string.
*   `Last Modified`: The exact timestamp from the `Last-Modified` HTTP header of that URL (if available, otherwise blank).
