from urllib.robotparser import RobotFileParser
import argparse
import asyncio
import aiohttp
from crawl import bfs_crawl
from urllib.parse import urlparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def get_robots_parser(seed_url):
    parsed = urlparse(seed_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    print("Robots URL:", robots_url)
    
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()  # fetch and parse robots.txt

    return rp

def reverse_graph(graph):
    reversed_graph = {}
    for url, links in graph.items():
        for link in links:
            if link not in reversed_graph:
                reversed_graph[link] = []
            reversed_graph[link].append(url)
    return reversed_graph

def broken_links(results):
    broken_links = []
    for url, res in results.items():
        if res["status"] == "ERROR" or res["status"] == 404:
            broken_links.append(url)
    return broken_links

def redirected_links(results):
    redirects = {}
    for url, res in results.items():
        if res["status"] in [301, 302]:
            redirects[url] = res.get("redirect_to")
    return redirects

def orphan_pages(results, reversed_graph, seed_url):
    all_pages = set(results.keys())
    inbound_pages = set(reversed_graph.keys())

    orphans = all_pages - inbound_pages

    # remove seed (it has no parent)
    if seed_url in orphans:
        orphans.remove(seed_url)

    return list(orphans)

def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")


def save_json(results, graph):
    if not results:
        return

    # Get domain from first URL
    first_url = next(iter(results))
    domain = get_domain(first_url)

    output_dir = Path("output") / domain
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "crawl_graph.json", "w") as f:
        json.dump({
            "results": results,
            "graph": graph
        }, f, indent=2)

    print(f"Crawl Graph saved to {output_dir / 'crawl_graph.json'}")


def generate_sitemap(results):
    if not results:
        return

    first_url = next(iter(results))
    domain = get_domain(first_url)

    output_dir = Path("output") / domain
    output_dir.mkdir(parents=True, exist_ok=True)

    urlset = ET.Element("urlset")

    for url in results.keys():
        url_tag = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_tag, "loc")
        loc.text = url

    tree = ET.ElementTree(urlset)
    tree.write(output_dir / "sitemap.xml", encoding="utf-8", xml_declaration=True)

    print(f"Sitemap saved to {output_dir / 'sitemap.xml'}")

async def main():
    parser = argparse.ArgumentParser(description="Web Crawler CLI")

    parser.add_argument("--url", required=True)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()

    print("Seed URL:", args.url)
    print("Max Depth:", args.depth)
    print("Concurrency:", args.concurrency)

    seed_url = args.url
    max_depth = args.depth
    concurrecny = args.concurrency
    rp = get_robots_parser(seed_url)

    async with aiohttp.ClientSession() as session:
        results, graph = await bfs_crawl(seed_url, max_depth, session, rp, concurrecny)
    
    print("\n=== Crawl Complete ===")
    print(f"Pages crawled: {len(results)}")
    print(f"Unique URLs: {len(graph)}")

    print("\n=== SEO Audit Report ===")

    # print("Results:")
    # for url, res in results.items():
    #     print(f"URL: {url}")
    #     print(f"Depth: {res['depth']}")
    #     print(f"Status: {res['status']}")
    #     print(f"Time: {res['time']:.2f}s")
    #     print(f"Links: {res['links']}")
    #     print()

    # print("Graph:")
    # for url, links in graph.items():
    #     print(f"URL: {url}")
    #     print(f"Links: {links}")
    #     print()

    reversed_graph = reverse_graph(graph)
    # print("Reversed Graph:")
    # for url, links in reversed_graph.items():
    #     print(f"URL: {url}")
    #     print(f"Links: {links}")
    #     print()

    brokenLinks = broken_links(results)
    print("Broken Links:")
    for link in brokenLinks:
        sources = reversed_graph.get(link, [])
        print(f"{link} (linked from: {sources})")

    redirectedLinks = redirected_links(results)
    print("Redirected Links:")
    for src, dest in redirectedLinks.items():
        print(f"{src} -> {dest}")

    orphans = orphan_pages(results, reversed_graph, seed_url)
    print("Orphan Pages:")
    for page in orphans:
        print(page)

    save_json(results, graph)  
    generate_sitemap(results)

if __name__ == "__main__":
    asyncio.run(main())