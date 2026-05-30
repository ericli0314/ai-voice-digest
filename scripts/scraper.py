import feedparser
import requests
import hashlib
from datetime import datetime, timedelta

TOPICS = [
    "Voice AI",
    "Voice Bot AI",
    "AI Agent customer service",
    "Agentic AI",
    "AI contact center",
    "conversational AI",
    "AI call center automation",
    "AI unified communications",
    "speech recognition AI enterprise",
    "large language model voice",
    "AI IVR telephony",
    "generative AI customer support",
]

EXTRA_RSS = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("The Verge AI", "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
]


def _article_id(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:10]


def fetch_google_news(query: str, max_items: int = 8) -> list[dict]:
    encoded = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:max_items]:
            results.append({
                "id": _article_id(entry.link),
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "topic": query,
                "source": "Google News",
            })
        return results
    except Exception as e:
        print(f"[scraper] Google News error for '{query}': {e}")
        return []


def fetch_hackernews(query: str, max_items: int = 10) -> list[dict]:
    since = int((datetime.utcnow() - timedelta(days=1)).timestamp())
    url = (
        "https://hn.algolia.com/api/v1/search"
        f"?query={query.replace(' ', '+')}"
        f"&tags=story&hitsPerPage={max_items}"
        f"&numericFilters=created_at_i>{since}"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        results = []
        for hit in resp.json().get("hits", []):
            link = hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}"
            results.append({
                "id": _article_id(link),
                "title": hit.get("title", ""),
                "link": link,
                "published": hit.get("created_at", ""),
                "summary": "",
                "topic": "Hacker News",
                "source": "Hacker News",
            })
        return results
    except Exception as e:
        print(f"[scraper] HN error for '{query}': {e}")
        return []


def fetch_rss(name: str, url: str, max_items: int = 8) -> list[dict]:
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:max_items]:
            results.append({
                "id": _article_id(entry.link),
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "topic": name,
                "source": name,
            })
        return results
    except Exception as e:
        print(f"[scraper] RSS error for '{name}': {e}")
        return []


def scrape_all() -> list[dict]:
    all_articles: list[dict] = []
    seen: set[str] = set()

    def add(articles):
        for a in articles:
            if a["id"] not in seen:
                seen.add(a["id"])
                all_articles.append(a)

    for topic in TOPICS:
        add(fetch_google_news(topic))

    add(fetch_hackernews("Voice AI OR AI Agent OR conversational AI OR agentic AI"))

    for name, url in EXTRA_RSS:
        add(fetch_rss(name, url))

    print(f"[scraper] Total unique articles: {len(all_articles)}")
    return all_articles
