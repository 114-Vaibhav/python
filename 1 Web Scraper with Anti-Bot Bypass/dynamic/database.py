import sqlite3

def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        date TEXT
    )
    """)
    
    conn.commit()
    conn.close()