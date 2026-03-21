"""
Weather API Integration - OpenWeatherMap
FREE TIER: 60 calls/min, 1 million calls/month

Usage:
    from core.weather_api import get_current_weather, get_5_day_forecast
    
    weather = get_current_weather("Springfield", "MO")
    forecast = get_5_day_forecast("Springfield", "MO")
"""

import os
import requests
from django.core.cache import cache


class WeatherAPI:
    """
    OpenWeatherMap API client for city weather data
    Includes caching to avoid hitting rate limits
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY', '')
        if not self.api_key:
            print("WARNING: WEATHER_API_KEY not set in environment variables")
    
    def get_current_weather(self, city_name, state_code):
        """
        Get current weather for a city
        Returns: {temp, feels_like, description, icon, humidity, wind_speed}
        """
        # Check cache first (cache for 10 minutes)
        cache_key = f"weather_current_{city_name}_{state_code}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Make API request
        url = f"{self.BASE_URL}/weather"
        params = {
            'q': f"{city_name},{state_code},US",
            'appid': self.api_key,
            'units': 'imperial'  # Fahrenheit
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            weather_data = {
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'icon_url': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed']),
                'pressure': data['main']['pressure'],
            }
            
            # Cache for 10 minutes
            cache.set(cache_key, weather_data, 600)
            return weather_data
            
        except requests.RequestException as e:
            print(f"Weather API error for {city_name}, {state_code}: {e}")
            return None
    
    def get_5_day_forecast(self, city_name, state_code):
        """
        Get 5-day forecast (3-hour intervals)
        Returns: List of daily forecasts with high/low temps
        """
        # Check cache first (cache for 30 minutes)
        cache_key = f"weather_forecast_{city_name}_{state_code}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Make API request
        url = f"{self.BASE_URL}/forecast"
        params = {
            'q': f"{city_name},{state_code},US",
            'appid': self.api_key,
            'units': 'imperial'
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Group by day and calculate high/low
            from datetime import datetime
            daily_forecasts = {}
            
            for item in data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                date_str = date.strftime('%Y-%m-%d')
                
                if date_str not in daily_forecasts:
                    daily_forecasts[date_str] = {
                        'date': date,
                        'day_name': date.strftime('%A'),
                        'temps': [],
                        'descriptions': [],
                        'icons': []
                    }
                
                daily_forecasts[date_str]['temps'].append(item['main']['temp'])
                daily_forecasts[date_str]['descriptions'].append(item['weather'][0]['description'])
                daily_forecasts[date_str]['icons'].append(item['weather'][0]['icon'])
            
            # Calculate high/low for each day
            forecast_list = []
            for date_str, day_data in list(daily_forecasts.items())[:5]:  # Only 5 days
                forecast_list.append({
                    'date': day_data['date'].strftime('%m/%d'),
                    'day_name': day_data['day_name'][:3],  # "Mon", "Tue", etc.
                    'high': round(max(day_data['temps'])),
                    'low': round(min(day_data['temps'])),
                    'description': max(set(day_data['descriptions']), key=day_data['descriptions'].count),
                    'icon': max(set(day_data['icons']), key=day_data['icons'].count),
                    'icon_url': f"http://openweathermap.org/img/wn/{max(set(day_data['icons']), key=day_data['icons'].count)}@2x.png"
                })
            
            # Cache for 30 minutes
            cache.set(cache_key, forecast_list, 1800)
            return forecast_list
            
        except requests.RequestException as e:
            print(f"Forecast API error for {city_name}, {state_code}: {e}")
            return []
    
    def get_coordinates_weather(self, latitude, longitude):
        """
        Get weather by GPS coordinates (backup method)
        """
        cache_key = f"weather_coords_{latitude}_{longitude}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        url = f"{self.BASE_URL}/weather"
        params = {
            'lat': latitude,
            'lon': longitude,
            'appid': self.api_key,
            'units': 'imperial'
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            weather_data = {
                'temp': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'description': data['weather'][0]['description'].title(),
                'icon_url': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            }
            
            cache.set(cache_key, weather_data, 600)
            return weather_data
            
        except requests.RequestException as e:
            print(f"Weather API error for coords {latitude},{longitude}: {e}")
            return None


# Singleton instance
_weather_api = None

def get_weather_api():
    """Get singleton WeatherAPI instance"""
    global _weather_api
    if _weather_api is None:
        _weather_api = WeatherAPI()
    return _weather_api


# Convenience functions
def get_current_weather(city_name, state_code):
    """Get current weother for a city"""
    api = get_weather_api()
    return api.get_current_weather(city_name, state_code)


def get_5_day_forecast(city_name, state_code):
    """Get 5-day forecast for a city"""
    api = get_weather_api()
    return api.get_5_day_forecast(city_name, state_code)
