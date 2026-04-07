import sqlite3
import random
from datetime import datetime, timedelta

# Connect to SQLite DB (creates file if not exists)
conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    region TEXT CHECK(region IN ('North','South','East','West')),
    revenue REAL,
    units_sold INTEGER
)
""")

regions = ['North', 'South', 'East', 'West']

# Function to generate random date in range
def random_dates(start_date, end_date, num_entries):
    delta = end_date - start_date
    return [
        start_date + timedelta(days=random.randint(0, delta.days))
        for _ in range(num_entries)
    ]

# Define 3 months range
start_date = datetime(2026, 1, 1)
end_date = datetime(2026, 3, 31)

# Generate ~75 entries (25 per month approx)
dates = random_dates(start_date, end_date, 75)

# Insert data
for d in dates:
    region = random.choice(regions)
    revenue = round(random.uniform(500, 5500), 2)
    units_sold = random.randint(1, 50)

    cursor.execute("""
    INSERT INTO sales (date, region, revenue, units_sold)
    VALUES (?, ?, ?, ?)
    """, (d.strftime('%Y-%m-%d'), region, revenue, units_sold))

# Commit and close
conn.commit()
conn.close()

print("✅ Dummy sales data generated successfully!")