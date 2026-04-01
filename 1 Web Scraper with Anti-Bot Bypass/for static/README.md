# 🕷️ Web Scraper with Anti-Bot Bypass

## 📌 Description

This project is a Python-based web scraper that extracts product data from an e-commerce website, stores it in a database, and generates a daily price comparison report.

---

## 🚀 Features

- Scrapes product name and price from multiple pages
- Handles pagination
- Stores data in SQLite database
- Compares daily price changes
- Generates CSV report
- Implements basic anti-bot techniques:
  - Random User-Agent rotation
  - Random delay between requests

---

## 🛠️ Tech Stack

- Python
- requests, BeautifulSoup
- SQLite
- pandas

---

## 📂 Project Structure

- `scraper.py` → Scraping logic
- `database.py` → Database storage
- `Report.py` → Price comparison
- `reports/` → Generated CSV reports

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python scraper.py
```

---

## 📊 Sample Output

- Logs:

```
[INFO] Scraping page 1
[INFO] 20 products extracted
[INFO] Sleeping for 4.23 seconds...
```

- Report:
  See `reports/sample_report.csv`

---

## 🧠 Learnings

- Web scraping fundamentals
- Database integration
- Data analysis and reporting
- Basic anti-bot techniques

---
