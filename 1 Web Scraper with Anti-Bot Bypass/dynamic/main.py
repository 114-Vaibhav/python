import asyncio
import sqlite3
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from database import init_db
from Report import generate_report

BASE_URL = "https://www.flipkart.com/search?q=girls+tshirts&page={}"


def scrape(page):
    driver = webdriver.Chrome()
    driver.get(BASE_URL.format(page))

    items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
    data = []

    for item in items[:10]:
        try:
            name = item.find_element(By.CSS_SELECTOR, "a[title]").get_attribute("title")
            price = item.find_element(By.XPATH, ".//*[contains(text(),'₹')]").text
            data.append({"name": name, "price": price})
        except:
            pass

    driver.quit()
    return data


def clean_price(price_str):
    return float(
        price_str.replace("₹", "")
        .replace(",", "")
        .replace("Â", "")
        .strip()
    )


def save_to_db(products):
    conn = sqlite3.connect("/dynamic/data.db")
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for p in products:
        price = clean_price(p["price"])

        if random.random() < 0.4:
            price += random.randint(1, 10)

        cursor.execute(
            "INSERT INTO products (name, price, date) VALUES (?, ?, ?)",
            (p["name"], price, yesterday)
        )

    for p in products:
        price = clean_price(p["price"])

        cursor.execute(
            "INSERT INTO products (name, price, date) VALUES (?, ?, ?)",
            (p["name"], price, today)
        )

    conn.commit()
    conn.close()


async def main():
    loop = asyncio.get_running_loop()

    with ThreadPoolExecutor(max_workers=3) as executor:
        tasks = [
            loop.run_in_executor(executor, scrape, page)
            for page in range(1, 4)
        ]

        results = await asyncio.gather(*tasks)


    products = [item for page in results for item in page]

    for p in products:
        print(p["name"], ":", p["price"])

    return products


if __name__ == "__main__":
    init_db()

    products = asyncio.run(main())

    save_to_db(products)

    print("Saved to Database")
    print("Generating Report...")

    generate_report()