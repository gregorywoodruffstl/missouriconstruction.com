"""
Grokipedia API Integration - Grok-powered Famous People Data
NEXT-LEVEL: Using xAI's Grok instead of boring Wikipedia!

Grokipedia (https://grokipedia.com/) uses Grok AI to provide:
- Famous people by location
- Real-time data vs static Wikipedia
- More engaging, conversational bios
- Photos and achievements

Usage:
    from core.grokipedia_api import get_famous_people_from_city
    
    people = get_famous_people_from_city("Springfield", "Missouri")
"""

import os
import requests
from django.core.cache import cache


class GrokipediaAPI:
    """
    Grokipedia API client for famous people data
    Uses xAI's Grok for intelligent, real-time responses
    """
    
    # NOTE: Update this URL when Grokipedia API docs are available
    # For now, we'll use a fallback approach querying Grok directly
    BASE_URL = "https://api.grokipedia.com/v1"  # Hypothetical - adjust when available
    
    def __init__(self):
        self.api_key = os.getenv('GROKIPEDIA_API_KEY', os.getenv('XAI_API_KEY', ''))
        if not self.api_key:
            print("WARNING: GROKIPEDIA_API_KEY or XAI_API_KEY not set")
    
    def get_famous_people_from_city(self, city_name, state_name, limit=10):
        """
        Get famous people born in or associated with a city
        
        Returns: List of {name, category, achievement, birth_year, photo_url, bio}
        """
        # Check cache first (cache for 24 hours - famous people don't change often)
        cache_key = f"grokipedia_{city_name}_{state_name}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # APPROACH 1: Try Grokipedia API (if available)
        try:
            # This is hypothetical - adjust based on actual Grokipedia API docs
            response = requests.get(
                f"{self.BASE_URL}/famous_people",
                params={
                    'city': city_name,
                    'state': state_name,
                    'limit': limit
                },
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Cache for 24 hours
                cache.set(cache_key, data.get('people', []), 86400)
                return data.get('people', [])
        except Exception as e:
            print(f"Grokipedia API unavailable, using fallback: {e}")
        
        # APPROACH 2: Fallback to xAI Grok API with custom prompt
        return self._query_grok_for_famous_people(city_name, state_name, limit)
    
    def _query_grok_for_famous_people(self, city_name, state_name, limit=10):
        """
        Fallback: Query xAI Grok directly with structured prompt
        """
        try:
            # xAI API endpoint (similar to OpenAI)
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'grok-beta',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a helpful assistant that provides structured data about famous people. Always respond with valid JSON.'
                        },
                        {
                            'role': 'user',
                            'content': f'''List the {limit} most famous people born in or raised in {city_name}, {state_name}.

For each person, provide:
- name: Full name
- category: One of (Actor, Musician, Athlete, Politician, Business Leader, Scientist, Artist, Writer, Historical Figure)
- achievement: Notable achievement (one sentence)
- birth_year: Year born
- bio: Short bio (2-3 sentences)

Respond with ONLY a JSON array, no other text. Example:
[
  {{"name": "Brad Pitt", "category": "Actor", "achievement": "Academy Award winner known for Fight Club, Once Upon a Time in Hollywood", "birth_year": 1963, "bio": "Born in Shawnee, Oklahoma but raised in Springfield, Missouri. One of Hollywood's most recognizable actors with decades of acclaimed performances."}}
]'''
                        }
                    ],
                    'temperature': 0.3,  # Lower temperature for more factual responses
                    'max_tokens': 2000
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Parse JSON response from Grok
                import json
                try:
                    # Extract JSON from markdown code blocks if present
                    if '```json' in content:
                        content = content.split('```json')[1].split('```')[0].strip()
                    elif '```' in content:
                        content = content.split('```')[1].split('```')[0].strip()
                    
                    people = json.loads(content)
                    
                    # Add placeholder photo URLs (could integrate with image search later)
                    for person in people:
                        person['photo_url'] = f"https://via.placeholder.com/150?text={person['name'].replace(' ', '+')}"
                    
                    # Cache for 24 hours
                    cache.set(f"grokipedia_{city_name}_{state_name}", people, 86400)
                    return people
                    
                except json.JSONDecodeError as e:
                    print(f"Failed to parse Grok JSON response: {e}")
                    print(f"Response: {content}")
                    return self._get_fallback_famous_people(city_name, state_name)
            else:
                print(f"Grok API error: {response.status_code}")
                return self._get_fallback_famous_people(city_name, state_name)
                
        except Exception as e:
            print(f"Grok API error: {e}")
            return self._get_fallback_famous_people(city_name, state_name)
    
    def _get_fallback_famous_people(self, city_name, state_name):
        """
        Hardcoded fallback data for common Springfields
        Used when APIs are unavailable
        """
        fallback_data = {
            'Springfield, Missouri': [
                {
                    'name': 'Brad Pitt',
                    'category': 'Actor',
                    'achievement': 'Academy Award winner, known for Fight Club, Once Upon a Time in Hollywood',
                    'birth_year': 1963,
                    'bio': 'Born in Shawnee, Oklahoma but raised in Springfield, Missouri. One of Hollywood\'s most recognizable actors.',
                    'photo_url': 'https://via.placeholder.com/150?text=Brad+Pitt'
                },
                {
                    'name': 'John Goodman',
                    'category': 'Actor',
                    'achievement': 'Emmy Award winner, known for Roseanne, The Big Lebowski',
                    'birth_year': 1952,
                    'bio': 'Born and raised in Springfield, Missouri. Versatile actor known for both comedy and drama.',
                    'photo_url': 'https://via.placeholder.com/150?text=John+Goodman'
                },
                {
                    'name': 'Kathleen Turner',
                    'category': 'Actor',
                    'achievement': 'Golden Globe winner, known for Romancing the Stone, Body Heat',
                    'birth_year': 1954,
                    'bio': 'Born in Springfield, Missouri. Iconic actress of the 1980s and 1990s.',
                    'photo_url': 'https://via.placeholder.com/150?text=Kathleen+Turner'
                },
                {
                    'name': 'Payne Stewart',
                    'category': 'Athlete',
                    'achievement': '3-time major champion, 1999 U.S. Open winner',
                    'birth_year': 1957,
                    'bio': 'Professional golfer from Springfield, Missouri. Tragically died in a plane crash in 1999.',
                    'photo_url': 'https://via.placeholder.com/150?text=Payne+Stewart'
                }
            ],
            'Springfield, Illinois': [
                {
                    'name': 'Abraham Lincoln',
                    'category': 'Historical Figure',
                    'achievement': '16th President of the United States',
                    'birth_year': 1809,
                    'bio': 'Though born in Kentucky, Lincoln lived in Springfield, IL for 24 years as a lawyer and politician before becoming president.',
                    'photo_url': 'https://via.placeholder.com/150?text=Abraham+Lincoln'
                },
                {
                    'name': 'Vachel Lindsay',
                    'category': 'Writer',
                    'achievement': 'American poet known for "The Congo" and "General Booth Enters Heaven"',
                    'birth_year': 1879,
                    'bio': 'Born and raised in Springfield, Illinois. Pioneer of modern American poetry.',
                    'photo_url': 'https://via.placeholder.com/150?text=Vachel+Lindsay'
                }
            ],
            'Springfield, Massachusetts': [
                {
                    'name': 'Dr. Seuss',
                    'category': 'Writer',
                    'achievement': 'Beloved children\'s author of The Cat in the Hat, Green Eggs and Ham',
                    'birth_year': 1904,
                    'bio': 'Born Theodor Seuss Geisel in Springfield, Massachusetts. Created iconic characters that defined childhood for generations.',
                    'photo_url': 'https://via.placeholder.com/150?text=Dr.+Seuss'
                },
                {
                    'name': 'Timothy Leary',
                    'category': 'Scientist',
                    'achievement': 'Psychologist and counterculture icon',
                    'birth_year': 1920,
                    'bio': 'Born in Springfield, Massachusetts. Known for psychedelic research and "Turn on, tune in, drop out."',
                    'photo_url': 'https://via.placeholder.com/150?text=Timothy+Leary'
                }
            ]
        }
        
        key = f"{city_name}, {state_name}"
        return fallback_data.get(key, [])


# Singleton instance
_grokipedia_api = None

def get_grokipedia_api():
    """Get singleton GrokipediaAPI instance"""
    global _grokipedia_api
    if _grokipedia_api is None:
        _grokipedia_api = GrokipediaAPI()
    return _grokipedia_api


# Convenience function
def get_famous_people_from_city(city_name, state_name, limit=10):
    """Get famous people from a city using Grokipedia"""
    api = get_grokipedia_api()
    return api.get_famous_people_from_city(city_name, state_name, limit)
