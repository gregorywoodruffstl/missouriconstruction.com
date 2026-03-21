"""
City News Feed — Seeking Springfield
=====================================
Pulls hyper-local news for each of the 22 Springfield cities using
Google News RSS (completely free, no API key required).

Every city gets a base query built from its name + state.  Cities that
have a well-known local "hook" (Bass Pro, Illinois government, Nascar,
etc.) get an additional topic-specific query so the feed stays
interesting.

Usage:
    from core.news_api import fetch_city_news, fetch_city_topic_news
    articles = fetch_city_news(city_obj, max_results=8)

Returns a list of dicts:
    {
        'title': str,
        'url':   str,
        'source': str,
        'published': datetime | None,
        'summary': str,
        'topic': str | None   # the custom topic label if applicable
    }

Results are cached 30 minutes in Django's cache framework.

Author: Gregory Woodruff | Cloud and Secure Limited | Seeking Springfield
"""

import hashlib
import logging
from datetime import datetime
from urllib.parse import quote_plus

import feedparser
from django.core.cache import cache

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


# ---------------------------------------------------------------------------
# Per-city topic keywords
# Notable subjects people associate with each Springfield
# ---------------------------------------------------------------------------
CITY_TOPICS = {
    # -- Missouri --
    "springfield-mo": [
        {
            "label": "Bass Pro Shops",
            "query": '"Bass Pro Shops" Springfield Missouri',
            "emoji": "🎣",
        },
        {
            "label": "Springfield Cardinals / Minor League",
            "query": '"Springfield Cardinals" baseball Missouri',
            "emoji": "⚾",
        },
        {
            "label": "Missouri State Bears",
            "query": '"Missouri State" Springfield athletics',
            "emoji": "🐻",
        },
    ],
    # -- Illinois --
    "springfield-il": [
        {
            "label": "Illinois Government & Politics",
            "query": 'Springfield Illinois government politics legislature',
            "emoji": "🏛️",
        },
        {
            "label": "Abraham Lincoln Heritage",
            "query": '"Abraham Lincoln" Springfield Illinois',
            "emoji": "🎩",
        },
        {
            "label": "Illinois State Fair",
            "query": '"Illinois State Fair" Springfield',
            "emoji": "🎡",
        },
    ],
    # -- Massachusetts --
    "springfield-ma": [
        {
            "label": "Basketball Hall of Fame",
            "query": '"Basketball Hall of Fame" Springfield Massachusetts',
            "emoji": "🏀",
        },
        {
            "label": "Springfield Thunderbirds / AHL",
            "query": '"Springfield Thunderbirds" hockey AHL',
            "emoji": "🏒",
        },
    ],
    # -- Ohio --
    "springfield-oh": [
        {
            "label": "Clark County / Wittenberg",
            "query": 'Springfield Ohio "Clark County" OR "Wittenberg University"',
            "emoji": "🎓",
        },
    ],
    # -- Tennessee --
    "springfield-tn": [
        {
            "label": "Robertson County / Agriculture",
            "query": 'Springfield Tennessee "Robertson County" agriculture tobacco',
            "emoji": "🌱",
        },
    ],
    # -- Virginia --
    "springfield-va": [
        {
            "label": "Northern Virginia / DC Metro",
            "query": 'Springfield Virginia "Fairfax County" OR "Northern Virginia"',
            "emoji": "🏙️",
        },
    ],
    # -- Oregon --
    "springfield-or": [
        {
            "label": "Lane County / Eugene Metro",
            "query": 'Springfield Oregon "Lane County" OR Eugene metro',
            "emoji": "🌲",
        },
    ],
    # -- Michigan --
    "springfield-mi": [
        {
            "label": "Calhoun County",
            "query": 'Springfield Michigan "Calhoun County" Battle Creek',
            "emoji": "🍎",
        },
    ],
    # -- Pennsylvania --
    "springfield-pa": [
        {
            "label": "Delaware County / Philly Suburbs",
            "query": 'Springfield Pennsylvania "Delaware County" suburb Philadelphia',
            "emoji": "🔔",
        },
    ],
    # -- Colorado --
    "springfield-co": [
        {
            "label": "Baca County / Southeast Colorado",
            "query": 'Springfield Colorado "Baca County" agriculture ranching',
            "emoji": "🌾",
        },
    ],
    # -- South Dakota --
    "springfield-sd": [
        {
            "label": "Bon Homme County",
            "query": 'Springfield "South Dakota" "Bon Homme County"',
            "emoji": "🐄",
        },
    ],
    # -- Nebraska --
    "springfield-ne": [
        {
            "label": "Sarpy County",
            "query": 'Springfield Nebraska "Sarpy County" Omaha suburb',
            "emoji": "🌽",
        },
    ],
    # -- Kentucky --
    "springfield-ky": [
        {
            "label": "Washington County Bourbon",
            "query": 'Springfield Kentucky "Washington County" bourbon whiskey',
            "emoji": "🥃",
        },
    ],
    # -- Minnesota --
    "springfield-mn": [
        {
            "label": "Brown County Agriculture",
            "query": 'Springfield Minnesota "Brown County" agriculture',
            "emoji": "🌻",
        },
    ],
    # -- Wisconsin --
    "springfield-wi": [
        {
            "label": "Dane County",
            "query": 'Springfield Wisconsin "Dane County" Madison suburb',
            "emoji": "🧀",
        },
    ],
}


# ---------------------------------------------------------------------------
# Core fetch function
# ---------------------------------------------------------------------------

def _build_google_news_url(query: str) -> str:
    return GOOGLE_NEWS_RSS.format(query=quote_plus(query))


def _parse_feed(url: str, topic_label: str | None = None, emoji: str = "📰") -> list[dict]:
    """Fetch and parse a Google News RSS feed. Returns list of article dicts."""
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries:
            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

            # Google News source appears in feed.feed.title or entry.source.title
            source = ""
            if hasattr(entry, "source") and hasattr(entry.source, "title"):
                source = entry.source.title
            elif hasattr(feed, "feed") and hasattr(feed.feed, "title"):
                source = feed.feed.title

            results.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "source": source,
                "published": published,
                "summary": entry.get("summary", "")[:200],
                "topic": topic_label,
                "emoji": emoji,
            })
        return results
    except Exception as exc:
        logger.warning("News feed fetch failed for %s: %s", url, exc)
        return []


def fetch_city_news(city, max_results: int = 8) -> list[dict]:
    """
    Pull general local news for a city.
    Uses Google News RSS — no API key needed.
    Results cached 30 minutes.
    """
    city_name = city.name
    state_abbr = city.state.abbreviation if city.state else ""
    state_name = city.state.name if city.state else ""

    cache_key = f"city_news_{city.id}_general"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Build a targeted local news query
    query = f'"{city_name}, {state_abbr}" news'
    url = _build_google_news_url(query)
    articles = _parse_feed(url, topic_label=None, emoji="📰")[:max_results]

    cache.set(cache_key, articles, 60 * 30)  # 30 minutes
    return articles


def fetch_city_topic_news(city, max_results_per_topic: int = 4) -> list[dict]:
    """
    Pull topic-specific news for cities that have notable local subjects
    (Bass Pro in Springfield MO, Lincoln heritage in Springfield IL, etc.).
    Returns a flat list ordered by topic, then date.
    Cached 30 minutes per city.
    """
    city_slug = city.slug if hasattr(city, "slug") else city.name.lower().replace(" ", "-")
    state_abbr = (city.state.abbreviation if city.state else "").lower()
    lookup_key = f"springfield-{state_abbr}"  # e.g. "springfield-mo"

    topics = CITY_TOPICS.get(lookup_key, [])
    if not topics:
        return []

    cache_key = f"city_news_{city.id}_topics"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    all_articles = []
    for topic in topics:
        url = _build_google_news_url(topic["query"])
        articles = _parse_feed(url, topic_label=topic["label"], emoji=topic.get("emoji", "📰"))
        all_articles.extend(articles[:max_results_per_topic])

    cache.set(cache_key, all_articles, 60 * 30)
    return all_articles


def has_city_topics(city) -> bool:
    """Quick check — does this city have custom topic keywords?"""
    state_abbr = (city.state.abbreviation if city.state else "").lower()
    return f"springfield-{state_abbr}" in CITY_TOPICS
