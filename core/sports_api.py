"""
Sports News API - ESPN RSS Feeds + Team Data
FREE: ESPN RSS feeds for college and professional sports

Usage:
    from core.sports_api import get_local_sports_teams, get_recent_sports_news
    
    teams = get_local_sports_teams("Springfield", "MO")
    news = get_recent_sports_news("Springfield", "MO")
"""

import os
import requests
import feedparser
from django.core.cache import cache


class SportsAPI:
    """
    Sports news and team data for cities
    Uses ESPN RSS feeds + hardcoded local team mappings
    """
    
    # ESPN RSS feeds
    ESPN_RSS_FEEDS = {
        'mlb': 'https://www.espn.com/espn/rss/mlb/news',
        'nfl': 'https://www.espn.com/espn/rss/nfl/news',
        'nba': 'https://www.espn.com/espn/rss/nba/news',
        'nhl': 'https://www.espn.com/espn/rss/nhl/news',
        'ncaaf': 'https://www.espn.com/espn/rss/ncf/news',
        'ncaab': 'https://www.espn.com/espn/rss/ncb/news',
    }
    
    # Local teams by city (expandable!)
    CITY_TEAMS = {
        'Springfield, Missouri': [
            {
                'name': 'Springfield Cardinals',
                'sport': 'Baseball',
                'league': 'Minor League Baseball (AA)',
                'affiliation': 'St. Louis Cardinals',
                'website': 'https://www.milb.com/springfield'
            },
            {
                'name': 'Missouri State Bears',
                'sport': 'Basketball',
                'league': 'NCAA Division I (Missouri Valley Conference)',
                'website': 'https://missouristatebears.com/'
            },
            {
                'name': 'Missouri State Bears Football',
                'sport': 'Football',
                'league': 'NCAA Division I FCS (Missouri Valley Conference)',
                'website': 'https://missouristatebears.com/sports/football'
            }
        ],
        'Springfield, Massachusetts': [
            {
                'name': 'Springfield Thunderbirds',
                'sport': 'Hockey',
                'league': 'AHL (American Hockey League)',
                'affiliation': 'St. Louis Blues',
                'website': 'https://www.springfieldthunderbirds.com/'
            },
            {
                'name': 'UMass Minutemen',
                'sport': 'Basketball',
                'league': 'NCAA Division I (Atlantic 10)',
                'website': 'https://umassathletics.com/'
            },
            {
                'name': 'UMass Minutemen Football',
                'sport': 'Football',
                'league': 'NCAA Division I FBS (Independent)',
                'website': 'https://umassathletics.com/sports/football'
            }
        ],
        'Springfield, Illinois': [
            {
                'name': 'Illinois Fighting Illini',
                'sport': 'Basketball',
                'league': 'NCAA Division I (Big Ten)',
                'website': 'https://fightingillini.com/sports/mens-basketball',
                'note': 'Located in nearby Champaign-Urbana'
            },
            {
                'name': 'Illinois State Redbirds',
                'sport': 'Basketball',
                'league': 'NCAA Division I (Missouri Valley Conference)',
                'website': 'https://goredbirds.com/',
                'note': 'Located in nearby Normal, IL'
            }
        ],
        'Springfield, Ohio': [
            {
                'name': 'Wittenberg Tigers',
                'sport': 'Football',
                'league': 'NCAA Division III (NCAC)',
                'website': 'https://wittenbergtigers.com/'
            }
        ],
        'Springfield, Oregon': [
            {
                'name': 'Oregon Ducks',
                'sport': 'Football',
                'league': 'NCAA Division I FBS (Big Ten)',
                'website': 'https://goducks.com/sports/football',
                'note': 'Located in nearby Eugene'
            }
        ]
    }
    
    def get_local_teams(self, city_name, state_name):
        """
        Get local sports teams for a city
        Returns: List of team dictionaries
        """
        key = f"{city_name}, {state_name}"
        return self.CITY_TEAMS.get(key, [])
    
    def get_recent_news(self, city_name, state_name, limit=5):
        """
        Get recent sports news relevant to a city
        Filters ESPN RSS by local teams
        """
        # Check cache first (cache for 30 minutes)
        cache_key = f"sports_news_{city_name}_{state_name}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        teams = self.get_local_teams(city_name, state_name)
        if not teams:
            return []
        
        # Get team names for filtering
        team_names = [team['name'].split()[-1] for team in teams]  # "Cardinals", "Bears", etc.
        team_names.extend([city_name])  # Include city name
        
        # Fetch from appropriate RSS feeds
        news_items = []
        leagues = set(team['sport'].lower() for team in teams)
        
        # Map sports to RSS feeds
        feed_map = {
            'baseball': 'mlb',
            'football': ['nfl', 'ncaaf'],
            'basketball': ['nba', 'ncaab'],
            'hockey': 'nhl'
        }
        
        feeds_to_check = []
        for sport in leagues:
            if sport in feed_map:
                feed_keys = feed_map[sport]
                if isinstance(feed_keys, list):
                    feeds_to_check.extend(feed_keys)
                else:
                    feeds_to_check.append(feed_keys)
        
        # Fetch and parse RSS feeds
        for feed_key in feeds_to_check:
            if feed_key not in self.ESPN_RSS_FEEDS:
                continue
            
            try:
                feed = feedparser.parse(self.ESPN_RSS_FEEDS[feed_key])
                
                for entry in feed.entries[:20]:  # Check last 20 entries
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    
                    # Check if any team name appears in title or summary
                    if any(team_name.lower() in title.lower() or team_name.lower() in summary.lower() 
                           for team_name in team_names):
                        news_items.append({
                            'title': title,
                            'summary': summary,
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'source': 'ESPN'
                        })
                        
                        if len(news_items) >= limit:
                            break
            except Exception as e:
                print(f"Error fetching {feed_key} RSS: {e}")
                continue
        
        # Cache for 30 minutes
        cache.set(cache_key, news_items[:limit], 1800)
        return news_items[:limit]
    
    def get_team_schedule(self, team_name):
        """
        Get upcoming games for a specific team
        This would require team-specific ESPN pages - placeholder for now
        """
        # TODO: Implement web scraping of team schedules
        return []


# Singleton instance
_sports_api = None

def get_sports_api():
    """Get singleton SportsAPI instance"""
    global _sports_api
    if _sports_api is None:
        _sports_api = SportsAPI()
    return _sports_api


# Convenience functions
def get_local_sports_teams(city_name, state_name):
    """Get local sports teams for a city"""
    api = get_sports_api()
    return api.get_local_teams(city_name, state_name)


def get_recent_sports_news(city_name, state_name, limit=5):
    """Get recent sports news for a city"""
    api = get_sports_api()
    return api.get_recent_news(city_name, state_name, limit)
