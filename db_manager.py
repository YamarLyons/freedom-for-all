from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, text
import os
import time
from dotenv import load_dotenv
import logging
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Use DATABASE_URL from environment (internal URL from Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine using internal URL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=True
)
metadata = MetaData()

# Define the articles table schema
articles = Table(
    "articles", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String),
    Column("link", String, unique=True),
    Column("source", String),
    Column("timestamp", Integer)
)

CACHE_DURATION = 40 * 60 * 60  # 2 days in seconds

def init_db():
    logger.info("Starting database initialization")
    with engine.begin() as connection:
        result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='articles');"))
        table_exists = result.scalar()

        logger.info(f"Table 'articles' exists: {table_exists}")

        if table_exists:
            existing_data = connection.execute(articles.select()).fetchall()
            logger.info("Renaming existing articles table to articles_old")
            connection.execute(text("ALTER TABLE articles RENAME TO articles_old"))
        else:
            existing_data = []

        logger.info("Creating the 'articles' table")
        metadata.create_all(connection)

        if existing_data:
            logger.info("Restoring existing data to new articles table")
            for row in existing_data:
                connection.execute(articles.insert().values(
                    id=row.id,
                    title=row.title,
                    link=row.link,
                    source=row.source,
                    timestamp=row.timestamp
                ))

        logger.info("Dropping old table if it exists")
        connection.execute(text("DROP TABLE IF EXISTS articles_old"))
    logger.info("Database initialization completed")

def fetch_cached_articles():
    cutoff = int(time.time()) - CACHE_DURATION
    with engine.connect() as connection:
        result = connection.execute(articles.select().where(articles.c.timestamp > cutoff))
        return [{"title": row.title, "link": row.link, "source": row.source} for row in result]

def save_articles_to_db(articles_list):
    timestamp = int(time.time())
    with engine.connect() as connection:
        for article in articles_list:
            existing_article = connection.execute(articles.select().where(articles.c.link == article['link'])).fetchone()
            if not existing_article:
                connection.execute(articles.insert().values(
                    title=article['title'],
                    link=article['link'],
                    source=article['source'],
                    timestamp=timestamp
                ))

def direct_db_test():
    try:
        # For psycopg2 fallback, parse from DATABASE_URL
        import urllib.parse as up
        up.uses_netloc.append("postgres")
        url = up.urlparse(DATABASE_URL)

        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        logger.info(f"Connected to PostgreSQL version: {db_version[0]}")
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        logger.error(f"An error occurred: {e}")
