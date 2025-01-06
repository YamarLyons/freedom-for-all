from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import feedparser
from db_manager import init_db, fetch_cached_articles, save_articles_to_db

app = Flask(__name__)
CORS(app)

rss_feeds = {
    "wsj": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "csm": "https://rss.csmonitor.com/feeds/all",
    "hill": "https://thehill.com/feed/?feed=partnerfeed-news-feed&format=rss",
    "san": "https://san.com/feed/",
    "nyt": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "pol": "https://www.politico.com/rss/politicopicks.xml",
    "cbs": "https://www.cbsnews.com/latest/rss/main",
    "fox": "https://moxie.foxnews.com/google-publisher/world.xml",
    "bre": "https://www.breitbart.com/feed/",
    "daily": "https://www.dailywire.com/rss.xml",
    "npr": "https://feeds.npr.org/1003/rss.xml",
    "newsweek": "https://www.newsweek.com/rss",
    "BBC": "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
    "WP": "https://feeds.washingtonpost.com/rss/rss_election-2012",
}

def get_articles(rss_feeds):
    articles = []
    seen_articles = set()
    for source, feed_url in rss_feeds.items():
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.title
            link = entry.link
            if link not in seen_articles and title not in seen_articles:
                seen_articles.add(link)
                seen_articles.add(title)
                articles.append({"title": title, "link": link, "source": source})
    return articles

@app.route("/fetch-articles")
def fetch_articles():
    search_query = request.args.get('search', '').lower()
    cached_articles = fetch_cached_articles()
    if not cached_articles:
        cached_articles = get_articles(rss_feeds)
        save_articles_to_db(cached_articles)

    # Filter articles server-side if search query is provided
    if search_query:
        cached_articles = [article for article in cached_articles if search_query in article['title'].lower()]
    
    return jsonify(cached_articles)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    init_db()
    app.run()
