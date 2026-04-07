from urllib.robotparser import RobotFileParser
import argparse
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import time
from collections import defaultdict

async def fetch_with_status(session, url):
    try:
        async with session.get(url, allow_redirects=True) as response:
            status = response.status
            final_url = str(response.url)
            if status == 200:
                html = await response.text()
                return html, status, final_url
            elif status == 301 or status == 302:
                final_url = str(response.url)
                return None, status, final_url
            elif status == 404:
                return None, status, final_url
            return None, status ,final_url
    except Exception:
        return None, "ERROR", None
      
def extract_links(html, base_url):
    links = []
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # normalize relative URLs
        url = urljoin(base_url, href)
        # remove fragment
        url = url.split("#")[0]
        links.append(url)
    return links

def is_same_domain(seed, url):
    return urlparse(seed).netloc == urlparse(url).netloc

async def bfs_crawl(seed_url, max_depth, session, rp, concurrency):
    

    queue = deque([(seed_url, 0)])
    visited = set()
    discovered = set([seed_url])

    results = {}
    graph = defaultdict(list)

    semaphore = asyncio.Semaphore(concurrency)

    async def process_url(current_url, depth):
        if not rp.can_fetch("*", current_url):
            print(f"Blocked by robots.txt: {current_url}")
            return None

        async with semaphore:
            start = time.time()
            html, status, final_url = await fetch_with_status(session, current_url)
            elapsed = time.time() - start

        # print(f"[DEPTH {depth}] {current_url} {status} {elapsed:.2f}s")

        links = []
        if html:
            links = extract_links(html, current_url)

        return {
            "url": current_url,
            "redirect_to": final_url,
            "depth": depth,
            "status": status,
            "time": elapsed,
            "links": links
        }

    while queue:
        level_size = len(queue)
        tasks = []
        # if is_same_domain(seed_url, link) and link not in discovered:
        # 🔥 process current BFS level concurrently
        for _ in range(level_size):
            url, depth = queue.popleft()

            if url in visited or depth > max_depth:
                continue

            visited.add(url)
            tasks.append(process_url(url, depth))

        responses = await asyncio.gather(*tasks)

        for res in responses:
            if not res:
                continue

            url = res["url"]
            results[url] = res
            graph[url] = res["links"]

            for link in res["links"]:
                if is_same_domain(seed_url, link) and link not in discovered:
                    discovered.add(link)
                    queue.append((link, res["depth"] + 1))
        

    return results, graph

