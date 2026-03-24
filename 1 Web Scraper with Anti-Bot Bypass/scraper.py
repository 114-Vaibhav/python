import requests
import time
import sqlite3
import random
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import init_db
from pprint import pprint
from Report import generate_report

USER_AGENTS = [
    # Chrome (Windows)
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    
    # Chrome (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    
    # Safari (Mac)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
    
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    
    # Mobile Chrome
    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    
    # iPhone Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Version/16.0 Mobile Safari/604.1"
]

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"


def save_to_db(products):

    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for p in products:
        price = float(p["price"].replace("£", "").replace("Â", "").strip())
        # Apply change to ~30% of products
        if random.random() < 0.4:
            increase = random.randint(1, 10)
            price += increase
        
        cursor.execute("""
        INSERT INTO products (name, price, date)
        VALUES (?, ?, ?)
        """, (p["name"], price, yesterday))

    for p in products:
        # price = float(p["price"].replace("£", ""))
        price = float(p["price"].replace("£", "").replace("Â", "").strip())
        cursor.execute("""
        INSERT INTO products (name, price, date)
        VALUES (?, ?, ?)
        """, (p["name"], price, today))
    
    conn.commit()
    conn.close()

def scrape_page(page):
    url = BASE_URL.format(page)
    
    headers = {
    "User-Agent": random.choice(USER_AGENTS)
    }
    print("Using User Agent",headers["User-Agent"]);
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    # print(response.content);
    soup = BeautifulSoup(response.text, "html.parser")
    # print(soup);
    products = []
    items = soup.select(".product_pod")
    # print(items);
    for item in items:
        name = item.h3.a["title"]
        price = item.select_one(".price_color").text
        
        products.append({
            "name": name,
            "price": price
        })
    
    return products

def main():
    all_products = []
    
    print("[START] Scraper started")
    
    for page in range(1, 6):  # scrape 5 pages first
        print(f"[INFO] Scraping page {page}")
        data = scrape_page(page)
        print(f"[INFO] {len(data)} products extracted")
        
        all_products.extend(data)
        
        delay = random.uniform(1, 10)
        print(f"[INFO] Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)
    
    print(f"[DONE] Total products: {len(all_products)}")
    
    return all_products

def fetch_products(limit):
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products LIMIT ?", (limit,))
    # cursor.execute("SELECT * FROM products",)
    rows = cursor.fetchall()
    
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    products = main()
    # print("\n=== SCRAPED DATA ===")
    # pprint(products)
    save_to_db(products)
    print("Saved to Database")
    print("Showing from database");
    temp = fetch_products(10)

    for row in temp:
        print(row)

    generate_report();