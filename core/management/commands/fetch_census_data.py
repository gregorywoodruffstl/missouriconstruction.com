"""
Django Management Command: Fetch Census Data

This command fetches demographic data from the U.S. Census Bureau API
and populates City models with FREE government data.

Usage:
    python manage.py fetch_census_data                    # All cities
    python manage.py fetch_census_data --site seekingspringfield.com  # One site
    python manage.py fetch_census_data --city "Springfield, IL"       # One city
    python manage.py fetch_census_data --force             # Overwrite existing data

Enterprise Features:
- Batch processing with progress tracking
- Error handling with retry logic
- Logging for debugging
- Dry-run mode for testing
- Stats reporting

Author: Gregory Woodruff | Cloud and Secure Limited
Course: youbetyourazure.com/courses/census-api-integration/module-3
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils import timezone
from core.models import City, Site
from core.census_api import CensusAPIClient, CensusAPIError
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch Census Bureau demographic data for cities (FREE $10K+ value)'
    
    def add_arguments(self, parser):
        """Command-line arguments"""
        
        parser.add_argument(
            '--site',
            type=str,
            help='Fetch data only for cities on this site (e.g., seekingspringfield.com)'
        )
        
        parser.add_argument(
            '--city',
            type=str,
            help='Fetch data for specific city (format: "City Name, ST")'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing Census data (default: skip cities with data)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
        
        parser.add_argument(
            '--api-key',
            type=str,
            help='Census API key (or set CENSUS_API_KEY environment variable)'
        )
    
    def handle(self, *args, **options):
        """Execute the command"""
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("🏛️  U.S. CENSUS DATA FETCHER"))
        self.stdout.write(self.style.SUCCESS("Free Government Data Worth $10,000+/Year"))
        self.stdout.write("=" * 80)
        
        # Initialize Census API client
        api_key = options.get('api_key')
        client = CensusAPIClient(api_key=api_key)
        
        if not client.api_key:
            self.stdout.write(
                self.style.WARNING(
                    "\n⚠️  No API key found. Get one FREE at: https://api.census.gov/data/key_signup.html"
                )
            )
            self.stdout.write("   Set with: --api-key YOUR_KEY or CENSUS_API_KEY environment variable\n")
        
        # Build query based on filters
        cities = self._get_cities(options)
        
        if not cities.exists():
            raise CommandError("No cities found matching criteria")
        
        total_cities = cities.count()
        self.stdout.write(f"\n📊 Found {total_cities} cities to process\n")
        
        # Confirm if force update
        if options['force']:
            self.stdout.write(self.style.WARNING("⚠️  FORCE mode: Will overwrite existing data\n"))
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("🧪 DRY RUN: No changes will be made\n"))
        
        # Process cities
        stats = {
            'processed': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'total_population': 0
        }
        
        for i, city in enumerate(cities, 1):
            self.stdout.write(f"\n[{i}/{total_cities}] Processing: {city.name}, {city.state}")
            
            # Skip if already has data (unless --force)
            if city.population and not options['force']:
                self.stdout.write(self.style.WARNING(f"  ⏭️  Skipping (already has data). Use --force to update."))
                stats['skipped'] += 1
                continue
            
            try:
                # Fetch Census data
                self.stdout.write("  🌐 Fetching from Census Bureau...")
                
                # Get two-letter state code from State object
                state_code = city.state.abbreviation if city.state else None
                if not state_code:
                    self.stdout.write(self.style.ERROR(f"  ❌ City has no state assigned"))
                    stats['errors'] += 1
                    continue
                
                census_data = client.fetch_city_data(city.name, state_code)
                
                if census_data.get('error'):
                    self.stdout.write(self.style.ERROR(f"  ❌ {census_data['error']}"))
                    stats['errors'] += 1
                    continue
                
                # Update city model (unless dry-run)
                if not options['dry_run']:
                    city.population = census_data.get('total_population')
                    city.median_income = census_data.get('median_household_income')
                    city.census_data = census_data
                    city.last_census_updated = timezone.now()
                    city.save()
                
                # Display results
                population = census_data.get('total_population', 'N/A')
                income = census_data.get('median_household_income', 'N/A')
                
                if income and income != 'N/A':
                    income_formatted = f"${income:,.0f}"
                else:
                    income_formatted = 'N/A'
                
                self.stdout.write(self.style.SUCCESS(f"  ✅ Population: {population:,} | Median Income: {income_formatted}"))
                
                stats['updated'] += 1
                stats['processed'] += 1
                
                if isinstance(population, int):
                    stats['total_population'] += population
                
            except CensusAPIError as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Census API Error: {str(e)}"))
                stats['errors'] += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Unexpected Error: {str(e)}"))
                logger.exception(f"Error processing {city.name}, {city.state}")
                stats['errors'] += 1
        
        # Print summary
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("📈 SUMMARY REPORT"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"Total Cities: {total_cities}")
        self.stdout.write(self.style.SUCCESS(f"✅ Updated: {stats['updated']}"))
        self.stdout.write(self.style.WARNING(f"⏭️  Skipped: {stats['skipped']}"))
        self.stdout.write(self.style.ERROR(f"❌ Errors: {stats['errors']}"))
        
        if stats['total_population'] > 0:
            self.stdout.write(f"\n🏙️  Total Population Covered: {stats['total_population']:,}")
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING("\n🧪 DRY RUN COMPLETE - No changes were made"))
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Census data fetch complete!"))
        
        self.stdout.write("=" * 80 + "\n")
    
    def _get_cities(self, options):
        """Build City queryset based on command options"""
        
        queryset = City.objects.all()
        
        # Filter by site
        if options.get('site'):
            site_domain = options['site']
            queryset = queryset.filter(sites__domain_name=site_domain)
        
        # Filter by specific city
        if options.get('city'):
            city_str = options['city']
            try:
                city_name, state = city_str.split(',')
                queryset = queryset.filter(
                    name__iexact=city_name.strip(),
                    state__iexact=state.strip()
                )
            except ValueError:
                raise CommandError(
                    f"Invalid city format: '{city_str}'. Use: 'City Name, ST'"
                )
        
        return queryset.select_related().prefetch_related('sites')
    
    def _get_state_code(self, state_name: str) -> str:
        """Convert state name to two-letter code"""
        
        STATE_CODES = {
            'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
            'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
            'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
            'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
            'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
            'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
            'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
            'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
            'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
            'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
            'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
            'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
            'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC', 'Puerto Rico': 'PR'
        }
        
        # Try exact match first
        if state_name in STATE_CODES:
            return STATE_CODES[state_name]
        
        # Try case-insensitive match
        for full_name, code in STATE_CODES.items():
            if full_name.lower() == state_name.lower():
                return code
        
        # If already a code, return it
        if len(state_name) == 2:
            return state_name.upper()
        
        return ''
