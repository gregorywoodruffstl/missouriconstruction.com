"""
Municipal Calendar Scraper — Seeking Springfield
================================================
Pulls civic events from the 22 Springfield cities into the platform's
Event model.  Three feed types are supported:

  ICAL    — icalendar (.ics) — most modern city sites publish one
  RSS     — feedparser ingestion of RSS/Atom event feeds
  SOCRATA — city open-data portals (Chicago, many Midwestern cities use these)

Usage (called automatically by the `fetch_city_events` management command):

    from core.calendar_scraper import scrape_source
    scrape_source(event_source_instance)

Author: Gregory Woodruff | Cloud and Secure Limited | Seeking Springfield
"""
import hashlib
import logging
import re
from datetime import datetime, timezone as dt_tz
from typing import List, Optional

import requests
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports — only import heavy libraries if they're installed
# ---------------------------------------------------------------------------
def _ical():
    try:
        import icalendar
        return icalendar
    except ImportError:
        raise ImportError(
            "icalendar is required for iCal feeds. "
            "Run: pip install icalendar"
        )

def _feedparser():
    try:
        import feedparser
        return feedparser
    except ImportError:
        raise ImportError(
            "feedparser is required for RSS feeds. "
            "Run: pip install feedparser"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fingerprint(city_id: int, title: str, start: datetime) -> str:
    """SHA-1 fingerprint used to deduplicate events."""
    raw = f"{city_id}|{title.strip().lower()}|{start.date().isoformat()}"
    return hashlib.sha1(raw.encode()).hexdigest()


def _ensure_aware(dt_val) -> Optional[datetime]:
    """
    Guarantee a timezone-aware datetime, or return None if conversion fails.
    """
    if dt_val is None:
        return None
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo is None:
            return dt_val.replace(tzinfo=dt_tz.utc)
        return dt_val
    # icalendar sometimes gives vDatetime (subclass), coerce to plain datetime
    try:
        from icalendar.prop import vDDDTypes
        if isinstance(dt_val, vDDDTypes):
            dt_val = dt_val.dt
    except Exception:
        pass
    if hasattr(dt_val, 'isoformat'):
        if hasattr(dt_val, 'date') and not hasattr(dt_val, 'hour'):
            # It's a date, not datetime
            return datetime(dt_val.year, dt_val.month, dt_val.day,
                            tzinfo=dt_tz.utc)
        return _ensure_aware(dt_val)
    return None


def _safe_slug(text: str, event_id: str) -> str:
    base = slugify(text)[:250]
    if not base:
        base = 'event'
    return f"{base}-{event_id[:8]}"


# ---------------------------------------------------------------------------
# iCal parser
# ---------------------------------------------------------------------------

def _parse_ical(content: bytes, source) -> List[dict]:
    """
    Parse an iCalendar file.  Returns a list of event dicts.
    """
    ical = _ical()
    cal = ical.Calendar.from_ical(content)
    events = []

    for component in cal.walk():
        if component.name != 'VEVENT':
            continue

        title = str(component.get('SUMMARY', '')).strip()
        if not title:
            continue

        dtstart = _ensure_aware(component.get('DTSTART', None))
        if not dtstart:
            continue
        dtend   = _ensure_aware(component.get('DTEND', None))

        uid = str(component.get('UID', hashlib.md5(title.encode()).hexdigest()))
        description = str(component.get('DESCRIPTION', '')).strip()
        location    = str(component.get('LOCATION', '')).strip()
        url         = str(component.get('URL', '')).strip()

        events.append({
            'title': title[:500],
            'description': description,
            'start': dtstart,
            'end': dtend,
            'location': location[:500],
            'event_url': url,
            'uid': uid,
        })

    return events


# ---------------------------------------------------------------------------
# RSS / Atom parser
# ---------------------------------------------------------------------------

def _parse_rss(content: bytes, source) -> List[dict]:
    """
    Parse an RSS or Atom feed.  Each entry becomes an event.
    Dates use published/updated times (not true event start times — close enough
    for the "what's happening today" use case).
    """
    fp = _feedparser()
    feed = fp.parse(content)
    events = []

    for entry in feed.entries:
        title = getattr(entry, 'title', '').strip()
        if not title:
            continue

        # Try multiple date fields
        start = None
        for date_attr in ('published_parsed', 'updated_parsed', 'created_parsed'):
            t = getattr(entry, date_attr, None)
            if t:
                try:
                    import time
                    start = datetime.fromtimestamp(
                        time.mktime(t), tz=dt_tz.utc
                    )
                    break
                except Exception:
                    pass

        if start is None:
            start = timezone.now()

        uid = getattr(entry, 'id', '') or getattr(entry, 'link', '') or title
        description = getattr(entry, 'summary', '') or ''
        url = getattr(entry, 'link', '') or ''

        events.append({
            'title': title[:500],
            'description': description,
            'start': start,
            'end': None,
            'location': '',
            'event_url': url,
            'uid': uid,
        })

    return events


# ---------------------------------------------------------------------------
# Socrata Open Data API parser
# ---------------------------------------------------------------------------

def _parse_socrata(url: str) -> List[dict]:
    """
    Pull events from a Socrata dataset.
    The URL should be a JSON endpoint, e.g.:
      https://data.springfield.il.us/resource/abc1-def2.json?$order=start_date+ASC&$limit=200

    We look for columns named: title/name, start_date, end_date, description,
    location, event_url — common in Socrata event datasets.
    """
    resp = requests.get(url, timeout=15, headers={'Accept': 'application/json'})
    resp.raise_for_status()
    rows = resp.json()
    events = []

    TITLE_KEYS   = ('title', 'name', 'event_name', 'summary')
    START_KEYS   = ('start_date', 'start_datetime', 'date', 'event_date', 'start')
    END_KEYS     = ('end_date', 'end_datetime', 'end')
    DESC_KEYS    = ('description', 'details', 'notes')
    LOC_KEYS     = ('location', 'address', 'venue')
    URL_KEYS     = ('url', 'link', 'event_url', 'website')

    for row in rows:
        title = ''
        for k in TITLE_KEYS:
            if row.get(k):
                title = str(row[k]).strip()
                break
        if not title:
            continue

        start = None
        for k in START_KEYS:
            raw = row.get(k)
            if raw:
                try:
                    from dateutil import parser as dp
                    start = dp.parse(str(raw))
                    if start.tzinfo is None:
                        start = start.replace(tzinfo=dt_tz.utc)
                    break
                except Exception:
                    pass

        if not start:
            start = timezone.now()

        end = None
        for k in END_KEYS:
            raw = row.get(k)
            if raw:
                try:
                    from dateutil import parser as dp
                    end = dp.parse(str(raw))
                    if end.tzinfo is None:
                        end = end.replace(tzinfo=dt_tz.utc)
                    break
                except Exception:
                    pass

        desc = ''
        for k in DESC_KEYS:
            if row.get(k):
                desc = str(row[k]).strip()
                break

        loc = ''
        for k in LOC_KEYS:
            if row.get(k):
                loc = str(row[k]).strip()
                break

        url = ''
        for k in URL_KEYS:
            if row.get(k):
                url = str(row[k]).strip()
                break

        uid = row.get(':id') or row.get('id') or hashlib.md5(
            f"{title}{start}".encode()
        ).hexdigest()

        events.append({
            'title': title[:500],
            'description': desc,
            'start': start,
            'end': end,
            'location': loc[:500],
            'event_url': url,
            'uid': str(uid),
        })

    return events


# ---------------------------------------------------------------------------
# HTML scraper (last resort)
# ---------------------------------------------------------------------------

def _parse_html(url: str, city_name: str) -> List[dict]:
    """
    Very basic HTML scrape — looks for <article> or <li> elements containing
    common event patterns.  This is intentionally minimal; city sites change
    their HTML frequently.  Better to upgrade to iCal when possible.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("beautifulsoup4 is required for HTML scraping. pip install beautifulsoup4")

    resp = requests.get(url, timeout=15, headers={
        'User-Agent': 'SeekingSpringfield/1.0 (civic calendar aggregator; contact=webmaster@seekingspringfield.com)'
    })
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    events = []
    # Try to find anything labelled "event" in class names
    candidates = (
        soup.find_all(class_=re.compile(r'event', re.I)) or
        soup.find_all('article') or
        soup.find_all('li', class_=re.compile(r'item|entry', re.I))
    )

    for el in candidates[:50]:  # Max 50 items per scrape
        title = ''
        for tag in ('h1', 'h2', 'h3', 'h4', 'a', 'strong'):
            t = el.find(tag)
            if t and t.get_text(strip=True):
                title = t.get_text(strip=True)[:500]
                break
        if not title:
            continue

        # Try to find a date string inside the element
        text = el.get_text(' ', strip=True)
        start = timezone.now()  # Default to today if no date found
        date_patterns = [
            r'\b(\w+ \d{1,2},?\s+\d{4})\b',          # March 15, 2026
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',         # 03/15/2026
            r'\b(\d{4}-\d{2}-\d{2})\b',                # 2026-03-15
        ]
        for pat in date_patterns:
            m = re.search(pat, text)
            if m:
                try:
                    from dateutil import parser as dp
                    start = dp.parse(m.group(1)).replace(tzinfo=dt_tz.utc)
                    break
                except Exception:
                    pass

        link_tag = el.find('a', href=True)
        href = link_tag['href'] if link_tag else ''
        if href and not href.startswith('http'):
            from urllib.parse import urljoin
            href = urljoin(url, href)

        uid = href or hashlib.md5(f"{city_name}{title}{start}".encode()).hexdigest()

        events.append({
            'title': title,
            'description': text[:1000],
            'start': start,
            'end': None,
            'location': '',
            'event_url': href,
            'uid': uid,
        })

    return events


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def scrape_source(source, site=None) -> dict:
    """
    Fetch and persist events for a single EventSource instance.

    Returns a summary dict:
        {'created': N, 'updated': N, 'skipped': N, 'errors': [...]}
    """
    from core.models import Event, Site as SiteModel

    if site is None:
        site = SiteModel.objects.filter(is_active=True).first()

    results = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': []}

    try:
        # Fetch raw content
        if source.feed_type == 'SOCRATA':
            raw_events = _parse_socrata(source.feed_url)
        elif source.feed_type == 'HTML':
            raw_events = _parse_html(source.feed_url, source.city.name)
        else:
            # ICAL or RSS — fetch bytes first
            resp = requests.get(source.feed_url, timeout=15, headers={
                'User-Agent': 'SeekingSpringfield/1.0 (civic calendar aggregator)'
            })
            resp.raise_for_status()
            content = resp.content

            if source.feed_type == 'ICAL':
                raw_events = _parse_ical(content, source)
            else:  # RSS
                raw_events = _parse_rss(content, source)

        now = timezone.now()

        for ev in raw_events:
            start = ev['start']
            if start < timezone.now().replace(year=timezone.now().year - 1):
                # Skip events older than 1 year
                results['skipped'] += 1
                continue

            fp = _make_fingerprint(source.city.id, ev['title'], start)

            # Deduplication: match on fingerprint OR uid
            existing = Event.objects.filter(
                city=source.city, fingerprint=fp
            ).first()

            if existing:
                # Update description/location if changed
                changed = False
                if ev['description'] and existing.description != ev['description']:
                    existing.description = ev['description']
                    changed = True
                if ev['end'] and existing.end_date != ev['end']:
                    existing.end_date = ev['end']
                    changed = True
                if changed:
                    existing.updated_at = now
                    existing.save(update_fields=['description', 'end_date', 'updated_at'])
                    results['updated'] += 1
                else:
                    results['skipped'] += 1
                continue

            # Build a unique slug
            base_slug = _safe_slug(ev['title'], fp)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            Event.objects.create(
                city=source.city,
                site=site,
                title=ev['title'],
                slug=slug,
                description=ev['description'],
                start_date=start,
                end_date=ev['end'],
                location=ev['location'],
                event_url=ev['event_url'],
                source_url=source.feed_url,
                source=source,
                fingerprint=fp,
                ai_scraped=True,
                organizer=source.municipal_office_name or source.name,
            )
            results['created'] += 1

        source.mark_success()

    except Exception as e:
        error_msg = str(e)
        logger.error("Error scraping %s: %s", source, error_msg)
        results['errors'].append(error_msg)
        source.mark_failure(error_msg)

    return results
