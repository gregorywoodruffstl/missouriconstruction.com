"""
Populate Springfields - Add all 24 Springfield cities to database

This command creates the city records for seekingspringfield.com and links them
to the site. After running this, you can fetch Census data and generate articles.

Usage:
    python manage.py populate_springfields
    python manage.py populate_springfields --dry-run

After population, run:
    python manage.py fetch_census_data --site seekingspringfield.com
    python manage.py generate_daily_content --site seekingspringfield.com --type city_guide

Course: youbetyourazure.com/courses/building-city-directories
"""

from django.core.management.base import BaseCommand
from core.models import Site, City, State


class Command(BaseCommand):
    help = 'Populate all 24 Springfield cities in the United States'
    
    # All 24 Springfields with state codes
    SPRINGFIELDS = [
        {'name': 'Springfield', 'state': 'IL', 'country': 'United States', 'note': 'State capital, home of Abraham Lincoln'},
        {'name': 'Springfield', 'state': 'MO', 'country': 'United States', 'note': 'Birthplace of Route 66'},
        {'name': 'Springfield', 'state': 'MA', 'country': 'United States', 'note': 'Birthplace of basketball'},
        {'name': 'Springfield', 'state': 'OH', 'country': 'United States', 'note': 'Clark County seat'},
        {'name': 'Springfield', 'state': 'OR', 'country': 'United States', 'note': 'Inspiration for The Simpsons'},
        {'name': 'Springfield', 'state': 'VA', 'country': 'United States', 'note': 'Northern Virginia suburb'},
        {'name': 'Springfield', 'state': 'TN', 'country': 'United States', 'note': 'Robertson County seat'},
        {'name': 'Springfield', 'state': 'VT', 'country': 'United States', 'note': 'Windsor County'},
        {'name': 'Springfield', 'state': 'GA', 'country': 'United States', 'note': 'Effingham County seat'},
        {'name': 'Springfield', 'state': 'NJ', 'country': 'United States', 'note': 'Union County township'},
        {'name': 'Springfield', 'state': 'PA', 'country': 'United States', 'note': 'Delaware County'},
        {'name': 'Springfield', 'state': 'SC', 'country': 'United States', 'note': 'Orangeburg County'},
        {'name': 'Springfield', 'state': 'KY', 'country': 'United States', 'note': 'Washington County seat'},
        {'name': 'Springfield', 'state': 'LA', 'country': 'United States', 'note': 'Livingston Parish'},
        {'name': 'Springfield', 'state': 'MI', 'country': 'United States', 'note': 'Calhoun County'},
        {'name': 'Springfield', 'state': 'MN', 'country': 'United States', 'note': 'Brown County'},
        {'name': 'Springfield', 'state': 'NE', 'country': 'United States', 'note': 'Sarpy County'},
        {'name': 'Springfield', 'state': 'NH', 'country': 'United States', 'note': 'Sullivan County'},
        {'name': 'Springfield', 'state': 'CO', 'country': 'United States', 'note': 'Baca County seat'},
        {'name': 'Springfield', 'state': 'FL', 'country': 'United States', 'note': 'Bay County'},
        {'name': 'Springfield', 'state': 'WV', 'country': 'United States', 'note': 'Hampshire County'},
        {'name': 'Springfield', 'state': 'SD', 'country': 'United States', 'note': 'Bon Homme County'},
        {'name': 'Springfield', 'state': 'AR', 'country': 'United States', 'note': 'Conway County'},
        {'name': 'Springfield', 'state': 'ID', 'country': 'United States', 'note': 'Bingham County'},
    ]
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without creating cities'
        )
    
    def handle(self, *args, **options):
        """Main execution"""
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("POPULATE SPRINGFIELDS"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        dry_run = options['dry_run']
        
        # Get or create seekingspringfield.com site
        if not dry_run:
            site, created = Site.objects.get_or_create(
                domain_name='seekingspringfield.com',
                defaults={
                    'site_type': 'SEEKING',
                    'display_name': 'Seeking Springfield',
                    'primary_color': '#2E7D32',  # Green for spring
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS("✅ Created site: seekingspringfield.com"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  Site already exists: seekingspringfield.com"))
        else:
            self.stdout.write(f"🔍 DRY RUN - Would create/verify site: seekingspringfield.com")
            site = None
        
        self.stdout.write("")
        self.stdout.write(f"📍 Processing 24 Springfield cities...")
        self.stdout.write("")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No cities will be created"))
            self.stdout.write("")
        
        # Stats tracking
        stats = {
            'created': 0,
            'existing': 0,
            'total': len(self.SPRINGFIELDS),
        }
        
        # Process each Springfield
        for i, springfield_data in enumerate(self.SPRINGFIELDS, 1):
            city_name = springfield_data['name']
            state = springfield_data['state']
            country = springfield_data['country']
            note = springfield_data['note']
            
            self.stdout.write(f"[{i}/24] {city_name}, {state}")
            
            if dry_run:
                self.stdout.write(f"   🔍 Would create: {city_name}, {state}")
                self.stdout.write(f"      Note: {note}")
                stats['created'] += 1
                continue
            
            # Get State object
            try:
                state_obj = State.objects.get(abbreviation=state)
            except State.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"   ❌ State {state} not found! Run populate_states first."))
                continue
            
            # Check if city exists
            city, created = City.objects.get_or_create(
                name=city_name,
                state=state_obj,
                country=country,
                defaults={'state_abbr': state},
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"   ✅ Created: {city_name}, {state}"))
                self.stdout.write(f"      {note}")
                stats['created'] += 1
            else:
                self.stdout.write(self.style.WARNING(f"   ⏭️  Already exists: {city_name}, {state}"))
                stats['existing'] += 1
            
            # Link to site
            if site and city:
                city.sites.add(site)
        
        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("📊 POPULATION SUMMARY"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"Total Springfields: {stats['total']}")
        self.stdout.write(f"Created: {stats['created']}")
        self.stdout.write(f"Already Existed: {stats['existing']}")
        self.stdout.write("")
        
        if not dry_run and stats['created'] > 0:
            self.stdout.write(self.style.SUCCESS("✅ All Springfields linked to seekingspringfield.com"))
            self.stdout.write("")
            self.stdout.write("🚀 NEXT STEPS:")
            self.stdout.write("")
            self.stdout.write("1. Fetch Census data:")
            self.stdout.write("   python manage.py fetch_census_data --site seekingspringfield.com")
            self.stdout.write("")
            self.stdout.write("2. Generate AI articles:")
            self.stdout.write("   python manage.py generate_daily_content --site seekingspringfield.com")
            self.stdout.write("")
            self.stdout.write("3. Export for Power BI:")
            self.stdout.write("   python manage.py export_census_data --site seekingspringfield.com --format powerbi")
            self.stdout.write("")
            self.stdout.write("4. Review in admin:")
            self.stdout.write("   http://localhost:8002/admin/core/city/")
            self.stdout.write("")
        
        self.stdout.write("=" * 80)
