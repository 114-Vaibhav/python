import pandas as pd
import sqlite3
from database import init_db
import os

def generate_report():
    conn = sqlite3.connect("data.db")
    
    df = pd.read_sql_query("SELECT * FROM products", conn)
    
    conn.close()
    
    # Compare last 2 days
    dates = sorted(df["date"].unique())
    
    if len(dates) < 2:
        print("Not enough data to compare")
        return
    
    today, yesterday = dates[-1], dates[-2]
    
    df_today = df[df["date"] == today]
    df_yesterday = df[df["date"] == yesterday]
    
    merged = pd.merge(df_today, df_yesterday, on="name", suffixes=("_new", "_old"))
    
    merged["change"] = ((merged["price_new"] - merged["price_old"]) / merged["price_old"]) * 100
    
    changes = merged[merged["price_new"] != merged["price_old"]]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(base_dir, "reports")

    os.makedirs(reports_dir, exist_ok=True)

    changes.to_csv(os.path.join(reports_dir, f"{today}.csv"), index=False)
    
    print(f"{len(changes)} price changes found")
    print(changes.head());

init_db();
generate_report();
