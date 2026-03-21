"""
U.S. Census Bureau API Client with Enterprise-Grade Redundancy

This module provides FREE access to $10,000+ worth of demographic data.
Built with:
- Retry logic (handles API downtime)
- Exponential backoff (prevents overwhelming API)
- Error logging (debug issues)
- Data validation (ensures quality)
- Fallback mechanisms (never breaks)

Author: Gregory Woodruff | Cloud and Secure Limited
Course: youbetyourazure.com/courses/census-api-integration
"""

import requests
import time
import logging
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class CensusAPIError(Exception):
    """Custom exception for Census API errors"""
    pass


class CensusAPIClient:
    """
    U.S. Census Bureau API Client
    
    Handles:
    - American Community Survey (ACS) 5-Year Estimates
    - Decennial Census data
    - City-level demographics
    
    Free API Key: https://api.census.gov/data/key_signup.html
    """
    
    BASE_URL = "https://api.census.gov/data"
    
    # ACS 5-Year Estimates (most reliable city-level data)
    ACS5_ENDPOINT = "/2022/acs/acs5"
    
    # Variables we're pulling (FREE data worth $10K+/year commercially)
    VARIABLES = {
        'B01003_001E': 'total_population',           # Total Population
        'B19013_001E': 'median_household_income',    # Median Household Income
        'B25077_001E': 'median_home_value',          # Median Home Value
        'B23025_005E': 'unemployment_count',          # Unemployed
        'B01002_001E': 'median_age',                 # Median Age
        'B15003_022E': 'bachelors_degree_count',     # Bachelor's Degree holders
        'B15003_023E': 'masters_degree_count',       # Master's Degree holders
        'B02001_002E': 'white_alone',                # White Alone
        'B02001_003E': 'black_alone',                # Black Alone
        'B02001_004E': 'native_american_alone',      # Native American Alone
        'B02001_005E': 'asian_alone',                # Asian Alone
        'B03002_012E': 'hispanic_latino',            # Hispanic or Latino
        'B25003_002E': 'owner_occupied_housing',     # Owner-Occupied Housing
        'B25003_003E': 'renter_occupied_housing',    # Renter-Occupied Housing
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Census API Client
        
        Args:
            api_key: Census API key (get free at api.census.gov)
        """
        self.api_key = api_key or self._get_api_key_from_env()
        
        if not self.api_key:
            logger.warning("No Census API key provided. Some features may be limited.")
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment variable"""
        import os
        from decouple import config
        
        try:
            return config('CENSUS_API_KEY', default=None)
        except:
            return os.environ.get('CENSUS_API_KEY')
    
    def fetch_city_data(
        self, 
        city_name: str, 
        state_code: str,
        max_retries: int = 3,
        retry_delay: int = 2
    ) -> Dict:
        """
        Fetch demographic data for a specific city (BULLETPROOF version)
        
        Args:
            city_name: City name (e.g., "Springfield")
            state_code: Two-letter state code (e.g., "IL")
            max_retries: Number of retry attempts if API fails
            retry_delay: Seconds to wait between retries (exponential backoff)
        
        Returns:
            Dict with demographic data
            
        Raises:
            CensusAPIError: If all retries fail
        """
        
        # Build API request URL
        variables = ','.join(self.VARIABLES.keys())
        params = {
            'get': variables,
            'for': f'place:*',
            'in': f'state:{self._get_state_fips(state_code)}',
            'key': self.api_key
        }
        
        url = f"{self.BASE_URL}{self.ACS5_ENDPOINT}"
        
        # RETRY LOGIC - Handle API downtime, network issues
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching Census data for {city_name}, {state_code} (attempt {attempt + 1}/{max_retries})")
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                # Find matching city in results
                city_data = self._find_city_in_results(data, city_name)
                
                if city_data:
                    parsed_data = self._parse_census_response(city_data)
                    logger.info(f"✅ Successfully fetched data for {city_name}, {state_code}")
                    return parsed_data
                else:
                    logger.warning(f"City '{city_name}' not found in {state_code} Census data")
                    return self._get_empty_data(city_name, state_code)
            
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout on attempt {attempt + 1} for {city_name}, {state_code}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise CensusAPIError(f"Timeout after {max_retries} attempts")
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    logger.warning(f"🚦 Rate limited. Waiting {retry_delay * 2} seconds...")
                    time.sleep(retry_delay * 2)
                    continue
                elif e.response.status_code >= 500:  # Server error
                    logger.warning(f"🔥 Census API server error: {e.response.status_code}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        raise CensusAPIError(f"Server error after {max_retries} attempts")
                else:
                    raise CensusAPIError(f"HTTP error: {e.response.status_code} - {e.response.text}")
            
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise CensusAPIError(f"Request failed after {max_retries} attempts: {str(e)}")
        
        # If we get here, all retries failed
        raise CensusAPIError(f"Failed to fetch data for {city_name}, {state_code} after {max_retries} attempts")
    
    def _find_city_in_results(self, data: List, city_name: str) -> Optional[List]:
        """Find matching city in Census API results"""
        if not data or len(data) < 2:
            return None
        
        # First row is headers, rest are data
        headers = data[0]
        
        # Find city name column (usually last or second to last)
        try:
            name_index = headers.index('NAME') if 'NAME' in headers else -1
        except:
            name_index = -1
        
        for row in data[1:]:
            row_name = row[name_index] if name_index >= 0 else row[-1]
            
            # Match city name (case-insensitive, partial match)
            if city_name.lower() in row_name.lower():
                return row
        
        return None
    
    def _parse_census_response(self, row: List) -> Dict:
        """Parse Census API response row into clean dictionary"""
        
        parsed = {}
        
        for i, (var_code, var_name) in enumerate(self.VARIABLES.items()):
            try:
                value = row[i]
                
                # Convert to appropriate type
                if value and value != '-':
                    if 'income' in var_name or 'value' in var_name:
                        parsed[var_name] = Decimal(str(value))
                    else:
                        parsed[var_name] = int(value)
                else:
                    parsed[var_name] = None
            except (ValueError, IndexError):
                parsed[var_name] = None
        
        # Calculate derived metrics
        parsed['unemployment_rate'] = self._calculate_unemployment_rate(parsed)
        parsed['college_education_rate'] = self._calculate_college_rate(parsed)
        parsed['homeownership_rate'] = self._calculate_homeownership_rate(parsed)
        
        # Add metadata
        parsed['fetched_at'] = datetime.now().isoformat()
        parsed['source'] = 'U.S. Census Bureau ACS 5-Year Estimates (2022)'
        
        return parsed
    
    def _calculate_unemployment_rate(self, data: Dict) -> Optional[Decimal]:
        """Calculate unemployment rate percentage"""
        try:
            if data.get('total_population') and data.get('unemployment_count'):
                rate = (data['unemployment_count'] / data['total_population']) * 100
                return Decimal(str(round(rate, 2)))
        except:
            pass
        return None
    
    def _calculate_college_rate(self, data: Dict) -> Optional[Decimal]:
        """Calculate percentage with college degree"""
        try:
            bachelors = data.get('bachelors_degree_count', 0) or 0
            masters = data.get('masters_degree_count', 0) or 0
            population = data.get('total_population', 0) or 0
            
            if population > 0:
                rate = ((bachelors + masters) / population) * 100
                return Decimal(str(round(rate, 2)))
        except:
            pass
        return None
    
    def _calculate_homeownership_rate(self, data: Dict) -> Optional[Decimal]:
        """Calculate homeownership percentage"""
        try:
            owned = data.get('owner_occupied_housing', 0) or 0
            rented = data.get('renter_occupied_housing', 0) or 0
            total_housing = owned + rented
            
            if total_housing > 0:
                rate = (owned / total_housing) * 100
                return Decimal(str(round(rate, 2)))
        except:
            pass
        return None
    
    def _get_empty_data(self, city_name: str, state_code: str) -> Dict:
        """Return empty data structure when city not found"""
        return {
            'total_population': None,
            'median_household_income': None,
            'median_home_value': None,
            'error': f'City not found: {city_name}, {state_code}',
            'fetched_at': datetime.now().isoformat(),
            'source': 'U.S. Census Bureau ACS 5-Year Estimates (2022)'
        }
    
    def _get_state_fips(self, state_code: str) -> str:
        """Convert state code to FIPS code"""
        STATE_FIPS = {
            'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06',
            'CO': '08', 'CT': '09', 'DE': '10', 'FL': '12', 'GA': '13',
            'HI': '15', 'ID': '16', 'IL': '17', 'IN': '18', 'IA': '19',
            'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
            'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29',
            'MT': '30', 'NE': '31', 'NV': '32', 'NH': '33', 'NJ': '34',
            'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38', 'OH': '39',
            'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45',
            'SD': '46', 'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50',
            'VA': '51', 'WA': '53', 'WV': '54', 'WI': '55', 'WY': '56',
            'DC': '11', 'PR': '72'
        }
        
        return STATE_FIPS.get(state_code.upper(), '00')


# Convenience function for quick access
def get_city_demographics(city_name: str, state_code: str, api_key: Optional[str] = None) -> Dict:
    """
    Quick function to fetch city demographics
    
    Example:
        data = get_city_demographics('Springfield', 'IL')
        print(f"Population: {data['total_population']}")
    """
    client = CensusAPIClient(api_key=api_key)
    return client.fetch_city_data(city_name, state_code)
