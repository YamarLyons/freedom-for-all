from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, text
import os
import time
from dotenv import load_dotenv
import logging
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Use PostgreSQL with SQLAlchemy
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)  # echo=True will log SQL statements for debugging
metadata = MetaData()  # Remove 'bind' from here

# Define the articles table schema for PostgreSQL
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
    """Initialize the PostgreSQL database with the correct schema."""
    logger.info("Starting database initialization")
    with engine.begin() as connection:  # Use 'begin' for automatic commit/rollback
        # Using `text()` for executing raw SQL queries correctly
        result = connection.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='articles');"))
        table_exists = result.scalar()

        logger.info(f"Table 'articles' exists: {table_exists}")

        # If the table exists, back up the data and recreate the schema
        if table_exists:
            existing_data = connection.execute(articles.select()).fetchall()
            logger.info("Renaming existing articles table to articles_old")
            connection.execute(text("ALTER TABLE articles RENAME TO articles_old"))
        else:
            existing_data = []

        logger.info("Creating the 'articles' table")
        metadata.create_all(connection)  # The connection here provides the bind

        # Restore existing data if available
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

        # Drop the old table if it existed
        logger.info("Dropping old table if it exists")
        connection.execute(text("DROP TABLE IF EXISTS articles_old"))
    logger.info("Database initialization completed")

def fetch_cached_articles():
    """Fetch articles that are still valid based on cache duration."""
    cutoff = int(time.time()) - CACHE_DURATION
    with engine.connect() as connection:
        result = connection.execute(articles.select().where(articles.c.timestamp > cutoff))
        return [{"title": row.title, "link": row.link, "source": row.source} for row in result]

def save_articles_to_db(articles_list):
    """Save the articles to the PostgreSQL database with the current timestamp."""
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
    """Function to test direct connection to the database using psycopg2."""
    try:
        # Parse the DATABASE_URL to get connection parameters
        connection_params = {
            'dbname': DATABASE_URL.split('//')[1].split(':')[0],
            'user': DATABASE_URL.split('//')[1].split(':')[1].split('@')[0],
            'password': DATABASE_URL.split('//')[1].split(':')[2].split('@')[0],
            'host': DATABASE_URL.split('@')[1].split(':')[0],
            'port': DATABASE_URL.split(':')[-1].split('/')[0]
        }
        
        conn = psycopg2.connect(**connection_params)
        cur = conn.cursor()
        
        # Example query to test if connection works
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        logger.info(f"Connected to PostgreSQL version: {db_version[0]}")
        
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        logger.error(f"An error occurred: {e}")

# Example usage (commented out to not run by default)
# init_db()
# print(fetch_cached_articles())
# direct_db_test()