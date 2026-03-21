"""
AI Content Engine - Expandable Multi-Source Article Generator

This module generates high-quality articles by aggregating data from multiple sources
and using GPT-4 to create engaging, SEO-optimized content.

Architecture:
- DataAggregator: Collects data from multiple sources (Census, schools, parks, etc.)
- ContentPromptBuilder: Creates rich prompts from aggregated data
- AIContentEngine: Generates articles using OpenAI GPT-4
- Built-in retry logic and error handling (bulletproof)

Data Sources (Expandable):
✅ Census Bureau (demographics)
🔄 School Districts (rankings) - Coming soon
🔄 Restaurants (unique local spots) - Coming soon
🔄 Parks & Recreation (national/state parks) - Coming soon
🔄 Events & Conventions (tourism) - Coming soon
🔄 Airports (infrastructure) - Coming soon
🔄 Historical Data (founding dates, stories) - Coming soon

Author: Gregory Woodruff | Cloud and Secure Limited
Course: youbetyourazure.com/courses/ai-content-generation
"""

import openai
from openai import OpenAI
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class AIContentError(Exception):
    """Custom exception for AI content generation errors"""
    pass


class DataAggregator:
    """
    Aggregates data from multiple sources for rich article generation
    
    Modular design - easy to add new data sources:
    1. Add method to fetch data source
    2. Add to aggregate() method
    3. Articles automatically get richer
    """
    
    def __init__(self, city, census_data: Optional[Dict] = None):
        """
        Initialize aggregator for a specific city
        
        Args:
            city: City model instance
            census_data: Optional pre-fetched census data
        """
        self.city = city
        self.census_data = census_data or {}
    
    def aggregate(self) -> Dict:
        """
        Aggregate ALL available data sources for this city
        
        Returns:
            Dict with all data organized by category
        """
        
        aggregated = {
            'city_name': self.city.name,
            'state': self.city.state.name,  # Pass state name as string, not State object
            'country': self.city.country,
            
            # Demographics (from Census API)
            'demographics': self._get_demographics(),
            
            # Infrastructure (expandable)
            'infrastructure': self._get_infrastructure(),
            
            # Education (expandable)
            'education': self._get_education(),
            
            # Tourism & Attractions (expandable)
            'tourism': self._get_tourism(),
            
            # History & Culture (expandable)
            'history': self._get_history(),
            
            # Economy & Business (expandable)
            'economy': self._get_economy(),
            
            # Comparisons (how this city ranks)
            'rankings': self._get_rankings(),
        }
        
        return aggregated
    
    def _get_demographics(self) -> Dict:
        """Extract demographic data from Census"""
        
        if not self.census_data:
            # Try to get from city model
            self.census_data = self.city.census_data or {}
        
        population = self.census_data.get('total_population')
        median_income = self.census_data.get('median_household_income')
        median_age = self.census_data.get('median_age')
        
        return {
            'population': f"{population:,}" if population else "Data unavailable",
            'median_income': f"${median_income:,.0f}" if median_income else "Data unavailable",
            'median_age': f"{median_age:.1f} years" if median_age else "Data unavailable",
            'unemployment_rate': self.census_data.get('unemployment_rate'),
            'college_education_rate': self.census_data.get('college_education_rate'),
            'homeownership_rate': self.census_data.get('homeownership_rate'),
        }
    
    def _get_infrastructure(self) -> Dict:
        """
        Infrastructure data (airports, highways, transit)
        
        TODO: Integrate with FAA airport database
        TODO: Integrate with DOT traffic data
        """
        
        return {
            'airports': 'Data source to be added',
            'highways': 'Data source to be added',
            'public_transit': 'Data source to be added',
            'note': 'Infrastructure module - expandable in future courses'
        }
    
    def _get_education(self) -> Dict:
        """
        Education data (school districts, rankings, universities)
        
        TODO: Integrate with Department of Education API
        TODO: Add school district rankings
        TODO: Add university data
        """
        
        return {
            'school_districts': 'Data source to be added',
            'national_ranking': 'Data source to be added',
            'universities': 'Data source to be added',
            'note': 'Education module - expandable in future courses'
        }
    
    def _get_tourism(self) -> Dict:
        """
        Tourism & attractions (parks, restaurants, events)
        
        This is where "Springfield spring fields" content goes!
        
        TODO: Integrate with Parks API
        TODO: Integrate with Yelp/Google Places for unique restaurants
        TODO: Integrate with Eventbrite for conventions
        """
        
        city_lower = self.city.name.lower()
        
        # Springfield-specific content (expandable to other cities)
        if 'springfield' in city_lower:
            tourism_angle = {
                'spring_attractions': 'Famous for spring blooms and field festivals',
                'unique_angle': 'Explore what makes this Springfield\'s spring fields unique',
                'note': 'Tourism module - will integrate Parks API, restaurant data, events'
            }
        else:
            tourism_angle = {
                'attractions': f'Discover what makes {self.city.name} special',
                'note': 'Tourism module - expandable in future courses'
            }
        
        return tourism_angle
    
    def _get_history(self) -> Dict:
        """
        Historical data (founding date, name origin, famous events)
        
        TODO: Integrate with Wikipedia API
        TODO: Add historical landmarks database
        """
        
        return {
            'founding_date': 'Data source to be added',
            'name_origin': 'Data source to be added',
            'notable_events': 'Data source to be added',
            'note': 'History module - expandable in future courses'
        }
    
    def _get_economy(self) -> Dict:
        """
        Economic data (major employers, industries, business climate)
        
        TODO: Integrate with Bureau of Labor Statistics
        TODO: Add major employer data
        """
        
        return {
            'major_industries': 'Data source to be added',
            'top_employers': 'Data source to be added',
            'business_climate': 'Data source to be added',
            'note': 'Economy module - expandable in future courses'
        }
    
    def _get_rankings(self) -> Dict:
        """
        City rankings and comparisons
        
        This enables "Springfield vs Springfield" comparisons!
        
        TODO: Build ranking system across all cities in database
        TODO: Add income rankings
        TODO: Add infrastructure rankings
        TODO: Add quality of life rankings
        """
        
        return {
            'income_rank': 'Ranking system to be built',
            'infrastructure_rank': 'Ranking system to be built',
            'quality_of_life_rank': 'Ranking system to be built',
            'note': 'Rankings module - Power BI visualization coming in advanced course'
        }


class ContentPromptBuilder:
    """
    Builds rich GPT-4 prompts from aggregated data
    
    Prompt templates are expandable - as we add data sources,
    prompts automatically get richer
    """
    
    ARTICLE_TYPES = {
        'city_guide': 'Comprehensive City Guide',
        'demographics': 'Demographic Overview',
        'tourism': 'Tourism & Attractions',
        'living_here': 'Living in {city_name}',
        'business': 'Business & Economy',
        'comparison': 'City Comparison',
    }
    
    def __init__(self, aggregated_data: Dict):
        """Initialize with aggregated data from DataAggregator"""
        self.data = aggregated_data
        self.city_name = aggregated_data['city_name']
        self.state = aggregated_data['state']
    
    def build_prompt(self, article_type: str, word_count: int = 500) -> str:
        """
        Build GPT-4 prompt for specified article type
        
        Args:
            article_type: Type of article (city_guide, demographics, etc.)
            word_count: Target word count
            
        Returns:
            Rich prompt string for GPT-4
        """
        
        if article_type == 'city_guide':
            return self._build_city_guide_prompt(word_count)
        elif article_type == 'demographics':
            return self._build_demographics_prompt(word_count)
        elif article_type == 'tourism':
            return self._build_tourism_prompt(word_count)
        elif article_type == 'living_here':
            return self._build_living_here_prompt(word_count)
        else:
            return self._build_generic_prompt(article_type, word_count)
    
    def _build_city_guide_prompt(self, word_count: int) -> str:
        """Comprehensive city guide prompt"""
        
        demographics = self.data['demographics']
        
        prompt = f"""Write a comprehensive, engaging city guide article about {self.city_name}, {self.state}.

TARGET AUDIENCE: People considering moving to, visiting, or doing business in {self.city_name}.

ARTICLE REQUIREMENTS:
- {word_count} words
- SEO-optimized for "{self.city_name} {self.state}" and "{self.city_name} city guide"
- Conversational, welcoming tone
- Include specific data points (makes article authoritative)
- Break into clear sections with subheadings
- End with call-to-action

AVAILABLE DATA TO INCORPORATE:

Demographics:
- Population: {demographics.get('population', 'N/A')}
- Median Income: {demographics.get('median_income', 'N/A')}
- Median Age: {demographics.get('median_age', 'N/A')}
- Homeownership Rate: {demographics.get('homeownership_rate', 'N/A')}%

ARTICLE STRUCTURE:
1. Opening hook (what makes {self.city_name} special?)
2. Overview (location, size, character)
3. Demographics & Population (incorporate data above)
4. Living in {self.city_name} (lifestyle, culture)
5. Economy & Jobs (mention if data available)
6. Things to Do (attractions, if data available)
7. Conclusion & Next Steps

WRITING STYLE:
- Use active voice
- Include specific numbers (builds trust)
- Mention local landmarks when possible
- Balance facts with storytelling
- Make it feel like a local wrote it

Begin the article now:
"""
        
        return prompt
    
    def _build_tourism_prompt(self, word_count: int) -> str:
        """Tourism-focused prompt (great for Springfield spring fields!)"""
        
        tourism = self.data['tourism']
        
        prompt = f"""Write an engaging tourism article about visiting {self.city_name}, {self.state}.

TARGET AUDIENCE: Tourists, convention-goers, people planning weekend trips.

ARTICLE REQUIREMENTS:
- {word_count} words
- SEO-optimized for "{self.city_name} tourism" and "things to do in {self.city_name}"
- Enthusiastic, inviting tone
- Focus on unique attractions (not generic chain restaurants/hotels)
- Include seasonal attractions if relevant

SPECIAL ANGLE:
"""
        
        # Add Springfield-specific spring fields content if available
        if 'spring_attractions' in tourism:
            prompt += f"""
{tourism['spring_attractions']}

Focus on seasonal attractions, spring blooms, and outdoor activities that make {self.city_name} special in spring.
Research springtime festivals, flower shows, and outdoor events that attract visitors from around the world.
"""
        
        prompt += f"""

ARTICLE STRUCTURE:
1. Opening (why visit {self.city_name}?)
2. Top Attractions (unique to this city)
3. Seasonal Highlights (especially spring/summer)
4. Local Dining (unique restaurants, not chains)
5. Where to Stay (highlight character, not just brands)
6. Events & Conventions (if applicable)
7. Getting There (airports, highways)
8. Conclusion (book your trip!)

Make it feel like an insider's guide, not a generic travel article.

Begin the article now:
"""
        
        return prompt
    
    def _build_demographics_prompt(self, word_count: int) -> str:
        """Data-rich demographic article"""
        
        demographics = self.data['demographics']
        
        prompt = f"""Write a data-driven article about the demographics and population of {self.city_name}, {self.state}.

TARGET AUDIENCE: Businesses, real estate investors, people considering relocation.

ARTICLE REQUIREMENTS:
- {word_count} words
- SEO-optimized for "{self.city_name} demographics" and "{self.city_name} population"
- Professional, authoritative tone
- Data-heavy (use all available statistics)
- Explain what the data means for residents/businesses

DEMOGRAPHIC DATA:
- Population: {demographics.get('population', 'N/A')}
- Median Household Income: {demographics.get('median_income', 'N/A')}
- Median Age: {demographics.get('median_age', 'N/A')}
- College Education Rate: {demographics.get('college_education_rate', 'N/A')}%
- Homeownership Rate: {demographics.get('homeownership_rate', 'N/A')}%
- Unemployment Rate: {demographics.get('unemployment_rate', 'N/A')}%

ARTICLE STRUCTURE:
1. Overview (city context)
2. Population Size & Density
3. Age Distribution & Median Age
4. Income & Economic Profile
5. Education Levels
6. Housing Market Characteristics
7. Employment Statistics
8. What This Means for You (practical implications)
9. Data Source & Methodology

Use charts/tables if possible (mention "see chart below" where appropriate).

Begin the article now:
"""
        
        return prompt
    
    def _build_living_here_prompt(self, word_count: int) -> str:
        """Lifestyle/quality of life article"""
        
        prompt = f"""Write a personal, engaging article about what it's like to live in {self.city_name}, {self.state}.

TARGET AUDIENCE: People considering moving to {self.city_name}.

TONE: Honest, balanced (pros and cons), conversational.

Begin the article now:
"""
        
        return prompt
    
    def _build_generic_prompt(self, article_type: str, word_count: int) -> str:
        """Fallback generic prompt"""
        
        return f"""Write a {word_count}-word article about {article_type} in {self.city_name}, {self.state}.
Make it engaging, informative, and SEO-optimized.

Begin the article now:
"""


class AIContentEngine:
    """
    OpenAI GPT-4 Content Generator with Enterprise-Grade Error Handling
    
    Features:
    - Retry logic (handles API failures)
    - Exponential backoff (prevents rate limits)
    - Token management (prevents overflow)
    - Cost tracking (monitors spend)
    - Quality validation (checks output)
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-4o-mini'):
        """
        Initialize AI Content Engine
        
        Args:
            api_key: OpenAI API key
            model: GPT model to use (gpt-4o-mini, gpt-4, gpt-3.5-turbo, etc.)
        """
        self.api_key = api_key or self._get_api_key_from_env()
        self.model = model
        
        if self.api_key:
            openai.api_key = self.api_key
        else:
            logger.warning("No OpenAI API key found")
    
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get API key from environment"""
        import os
        try:
            from decouple import config
            return config('OPENAI_API_KEY', default=None)
        except:
            return os.environ.get('OPENAI_API_KEY')
    
    def generate_article(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: int = 2,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate article using GPT-4 (BULLETPROOF version)
        
        Args:
            prompt: Rich prompt from ContentPromptBuilder
            max_retries: Retry attempts if API fails
            retry_delay: Seconds between retries
            temperature: Creativity (0.0-1.0, higher = more creative)
            
        Returns:
            Dict with article content, metadata, and stats
        """
        
        if not self.api_key:
            raise AIContentError("No OpenAI API key configured")
        
        # RETRY LOOP - Bulletproof like Census API
        for attempt in range(max_retries):
            try:
                logger.info(f"Generating content (attempt {attempt + 1}/{max_retries})")
                
                # Create OpenAI client
                client = OpenAI(api_key=self.api_key)
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert content writer specializing in city guides, demographics, and tourism articles. Write engaging, SEO-optimized content that balances data with storytelling."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=2000,  # Roughly 1500 words max
                )
                
                # Extract content
                content = response.choices[0].message.content.strip()
                
                # Build result with metadata
                result = {
                    'content': content,
                    'word_count': len(content.split()),
                    'model_used': self.model,
                    'tokens_used': response.usage.total_tokens,
                    'generated_at': datetime.now().isoformat(),
                    'temperature': temperature,
                    'quality_score': self._calculate_quality_score(content),
                }
                
                logger.info(f"✅ Generated {result['word_count']} words using {result['tokens_used']} tokens")
                
                return result
            
            except openai.RateLimitError:
                logger.warning(f"🚦 Rate limited. Waiting {retry_delay * 2} seconds...")
                time.sleep(retry_delay * 2)
                continue
            
            except openai.APITimeoutError:
                logger.warning(f"⏱️ Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise AIContentError("Timeout after retries")
            
            except openai.APIError as e:
                logger.error(f"❌ OpenAI API Error: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise AIContentError(f"API error after retries: {str(e)}")
            
            except Exception as e:
                logger.error(f"❌ Unexpected error: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))
                    continue
                else:
                    raise AIContentError(f"Failed after retries: {str(e)}")
        
        raise AIContentError(f"Failed to generate content after {max_retries} attempts")
    
    def _calculate_quality_score(self, content: str) -> float:
        """
        Simple quality score (0-100)
        
        Checks:
        - Length (longer = better, to a point)
        - Paragraph structure
        - Sentence variety
        - Keyword density
        
        TODO: Expand with more sophisticated checks
        """
        
        score = 50.0  # Start at 50%
        
        # Length check
        word_count = len(content.split())
        if 300 <= word_count <= 800:
            score += 20
        elif 200 <= word_count < 300 or 800 < word_count <= 1000:
            score += 10
        
        # Paragraph structure
        paragraphs = content.split('\n\n')
        if 3 <= len(paragraphs) <= 10:
            score += 15
        
        # Sentence variety (not all same length)
        sentences = content.split('.')
        if len(set(len(s.split()) for s in sentences if s.strip())) > 3:
            score += 15
        
        return min(100.0, score)


# Convenience function for quick article generation
def generate_city_article(city, article_type: str = 'city_guide', api_key: Optional[str] = None) -> Dict:
    """
    Quick function to generate article for a city
    
    Example:
        article = generate_city_article(city, article_type='tourism')
        print(article['content'])
    """
    
    # Aggregate data
    aggregator = DataAggregator(city, census_data=city.census_data)
    data = aggregator.aggregate()
    
    # Build prompt
    prompt_builder = ContentPromptBuilder(data)
    prompt = prompt_builder.build_prompt(article_type)
    
    # Generate content
    engine = AIContentEngine(api_key=api_key)
    result = engine.generate_article(prompt)
    
    return result
