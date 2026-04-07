# Concurrent Web Crawler with Depth Control

An asynchronous Python web crawler that explores a site level by level using breadth-first search (BFS), respects `robots.txt`, limits crawl depth, and controls request concurrency.

The crawler also generates a small SEO-style audit report with:

- broken links
- redirected links
- orphan pages
- a crawl graph in JSON
- a sitemap in XML

## Features

- Async crawling with `aiohttp`
- BFS traversal with configurable max depth
- Concurrency limiting with `asyncio.Semaphore`
- `robots.txt` checking before fetching a page
- Same-domain crawl restriction
- Link extraction using BeautifulSoup
- Crawl graph export as JSON
- Sitemap generation as XML
- Simple audit output for broken, redirected, and orphan pages

## Project Structure

```text
.
|-- main.py           # CLI entry point, reporting, JSON/XML export
|-- crawl.py          # BFS crawler implementation
|-- testCommands.txt  # sample commands
|-- output/           # generated crawl results
```

## Requirements

- Python 3.10+

Install dependencies:

```bash
pip install aiohttp beautifulsoup4
```

## How It Works

1. The crawler starts from a seed URL.
2. It fetches pages breadth-first, one depth level at a time.
3. Only links from the same domain are added back into the crawl queue.
4. Before fetching any URL, it checks whether crawling is allowed by `robots.txt`.
5. For each visited page, it records:
   - URL
   - final URL after redirect handling
   - depth
   - status code
   - response time
   - extracted links
6. After crawling, it prints a report and saves:
   - `output/<domain>/crawl_graph.json`
   - `output/<domain>/sitemap.xml`

## Usage

Run the crawler from the project folder:

```bash
python main.py --url <seed_url> --depth <max_depth> --concurrency <workers>
```

### Arguments

- `--url`: starting URL to crawl (required)
- `--depth`: maximum BFS depth to crawl, default is `2`
- `--concurrency`: maximum number of concurrent requests, default is `5`

### Examples

```bash
python main.py --url http://books.toscrape.com/ --depth 1 --concurrency 20
python main.py --url http://the-internet.herokuapp.com/status_codes --depth 2
```

## Example Output

```text
Seed URL: http://the-internet.herokuapp.com/status_codes
Max Depth: 2
Concurrency: 5
Robots URL: http://the-internet.herokuapp.com/robots.txt

=== Crawl Complete ===
Pages crawled: 5
Unique URLs: 5

=== SEO Audit Report ===
Broken Links:
http://the-internet.herokuapp.com/status_codes/404

Redirected Links:
http://the-internet.herokuapp.com/status_codes/301 -> http://the-internet.herokuapp.com/status_codes/301
```

## Output Files

### `crawl_graph.json`

Saved under:

```text
output/<domain>/crawl_graph.json
```

This file contains:

- `results`: per-page crawl metadata
- `graph`: adjacency list of extracted links

### `sitemap.xml`

Saved under:

```text
output/<domain>/sitemap.xml
```

It contains all crawled URLs as XML `<loc>` entries.

## SEO Audit Checks

The current report includes:

- `Broken Links`: pages that returned `404` or failed with `ERROR`
- `Redirected Links`: pages that returned `301` or `302`
- `Orphan Pages`: crawled pages with no inbound links from other crawled pages, excluding the seed URL
