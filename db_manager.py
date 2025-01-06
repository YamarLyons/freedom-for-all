import sqlite3
import time

DB_FILE = "articles.db"
CACHE_DURATION = 40 * 60 * 60  # 2 days

def init_db():
    """Recreate the 'articles' table with the correct schema."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if the 'articles' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
    table_exists = cursor.fetchone()

    if table_exists:
        # Backup the existing data, if any
        cursor.execute("SELECT id, title, link, source, timestamp FROM articles")
        existing_data = cursor.fetchall()

        # Rename the old table only if necessary (on schema changes)
        cursor.execute("ALTER TABLE articles RENAME TO articles_old")
    else:
        existing_data = []

    # Recreate the table with the correct schema
    cursor.execute("""
        CREATE TABLE articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT,
            source TEXT,
            timestamp INTEGER
        )
    """)

    # Migrate existing data into the new table
    if existing_data:
        cursor.executemany("""
            INSERT INTO articles (id, title, link, source, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, existing_data)

    # Drop the old table, if it exists
    cursor.execute("DROP TABLE IF EXISTS articles_old")

    conn.commit()
    conn.close()

def fetch_cached_articles():
    """Fetch articles that are still valid based on cache duration."""
    conn = sqlite3.connect(DB_FILE)
    cutoff = int(time.time()) - CACHE_DURATION
    cursor = conn.cursor()
    cursor.execute("SELECT title, link, source FROM articles WHERE timestamp > ?", (cutoff,))
    rows = cursor.fetchall()
    conn.close()
    
    return [{"title": row[0], "link": row[1], "source": row[2]} for row in rows]

def save_articles_to_db(articles):
    """Save the articles to the database with the current timestamp."""
    timestamp = int(time.time())
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for article in articles:
            cursor.execute("SELECT COUNT(*) FROM articles WHERE link = ?", (article['link'],))
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO articles (title, link, source, timestamp) VALUES (?, ?, ?, ?)", 
                    (article['title'], article['link'], article['source'], timestamp)
                )
        conn.commit()
