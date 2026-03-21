"""
Seed Missouri Construction — core content for launch

Creates:
  - missouriconstruction.com Site record
  - Missouri State record
  - St. Louis City record
  - Busch Stadium III project (flagship)
  - 10 major Missouri construction projects
  - 5 open bid opportunities
  - 5 recent permit records
  - Sunday launch article (the story — Cardinals share-worthy)
  - Cardinals Fan Hall of Fame pitch article

Usage:
    python manage.py seed_mocon_content
    python manage.py seed_mocon_content --dry-run
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
import datetime


class Command(BaseCommand):
    help = 'Seed Missouri Construction with launch content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be created without saving to database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write('=' * 72)
        self.stdout.write('SEED MISSOURI CONSTRUCTION — LAUNCH CONTENT')
        self.stdout.write('=' * 72)

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN — nothing will be saved\n'))

        from core.models import Site, State, City
        from construction.models import (
            ProjectCategory, Project, BidOpportunity, PermitRecord
        )

        # ── Site ──────────────────────────────────────────────────────────────
        self.stdout.write('\n[1/6] Site record')
        site_data = {
            'domain_name': 'missouriconstruction.com',
            'site_type': 'INDUSTRY',
            'display_name': 'Missouri Construction',
            'primary_color': '#1f2937',
            'is_active': True,
            'launch_date': datetime.date.today(),
        }
        if dry_run:
            self.stdout.write(f'  Would create: {site_data["domain_name"]}')
            site = None
        else:
            site, created = Site.objects.get_or_create(
                domain_name='missouriconstruction.com',
                defaults=site_data,
            )
            verb = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'  {verb}: missouriconstruction.com'))

        # ── State ─────────────────────────────────────────────────────────────
        self.stdout.write('\n[2/6] Missouri state record')
        mo_data = {
            'name': 'Missouri',
            'abbreviation': 'MO',
            'capital': 'Jefferson City',
            'state_flower': 'White Hawthorn Blossom',
            'state_tree': 'Flowering Dogwood',
            'state_bird': 'Eastern Bluebird',
            'state_motto': 'Salus populi suprema lex esto',
            'region': 'Midwest',
        }
        if dry_run:
            self.stdout.write('  Would create: Missouri (MO)')
            mo_state = None
        else:
            mo_state, created = State.objects.get_or_create(
                abbreviation='MO',
                defaults=mo_data,
            )
            verb = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'  {verb}: Missouri'))

        # ── City ──────────────────────────────────────────────────────────────
        self.stdout.write('\n[3/6] St. Louis city record')
        if dry_run:
            self.stdout.write('  Would create: St. Louis, MO')
            stl = None
        else:
            stl, created = City.objects.get_or_create(
                name='St. Louis',
                state=mo_state,
                defaults={
                    'state_abbr': 'MO',
                    'country': 'USA',
                    'population': 301578,
                    'latitude': 38.6270,
                    'longitude': -90.1994,
                },
            )
            verb = 'Created' if created else 'Already exists'
            self.stdout.write(self.style.SUCCESS(f'  {verb}: St. Louis'))

        # ── Project Categories ─────────────────────────────────────────────
        self.stdout.write('\n[4/6] Project categories')
        categories = [
            ('Sports & Entertainment', 0),
            ('Infrastructure & Bridges', 1),
            ('Commercial Development', 2),
            ('Residential Development', 3),
            ('Healthcare', 4),
            ('Education', 5),
            ('Government & Civic', 6),
            ('Conservation & Wildlife', 7),
        ]
        cat_map = {}
        for name, order in categories:
            if dry_run:
                self.stdout.write(f'  Would create: {name}')
            else:
                cat, created = ProjectCategory.objects.get_or_create(
                    slug=slugify(name),
                    defaults={'name': name, 'order': order},
                )
                cat_map[name] = cat
                verb = 'Created' if created else 'Exists'
                self.stdout.write(f'  {verb}: {name}')

        # ── Projects ──────────────────────────────────────────────────────────
        self.stdout.write('\n[5/6] Projects')

        projects = [
            {
                'title': 'Busch Stadium III — Construction Documentation',
                'slug': 'busch-stadium-iii',
                'category': 'Sports & Entertainment',
                'location': '700 Clark Ave',
                'city': 'St. Louis',
                'state': 'MO',
                'description': (
                    'Three years. Hundreds of visits. Thousands of photographs.\n\n'
                    'Beginning on Day 1 of demolition, Gregory Woodruff documented every phase '
                    'of Busch Stadium III\'s construction — from the moment the final light poles '
                    'of the old park came down to the ribbon-cutting on Opening Day 2006.\n\n'
                    'Standing at the south end of the old stadium, at the exact spot where home plate '
                    'would sit in the new park, Woodruff photographed something no construction '
                    'photographer had ever captured at any other Major League Baseball facility: '
                    'a direct, unobstructed view of the Gateway Arch — the 630-foot stainless-steel '
                    'Jefferson National Expansion Memorial — framed perfectly by the rising steel skeleton '
                    'of the new stadium. No building in St. Louis is permitted to stand taller than the '
                    'Arch. Busch Stadium III honors that. The view remains today.\n\n'
                    'This is the only Major League Baseball park in America with a direct sightline '
                    'to a National Monument.\n\n'
                    'The full gallery — organized by construction phase and season — documents '
                    'the human story behind the steel: union electricians from Worn Signs running '
                    'cable in subzero January mornings, ironworkers completing the upper deck before '
                    'the last home game of the 2005 season, and the quiet, magnificent morning when '
                    'the last piece of the facade was set into place.'
                ),
                'contractor': 'Hunt Construction Group (General Contractor)',
                'owner': 'St. Louis Cardinals LLC',
                'architect': 'HOK Sport (now Populous)',
                'status': 'completed',
                'start_date': datetime.date(2004, 1, 17),
                'end_date': datetime.date(2006, 4, 10),
                'estimated_cost': 365000000,
                'featured': True,
            },
            {
                'title': 'NGA National Geospatial-Intelligence Agency Campus',
                'slug': 'nga-campus-st-louis',
                'category': 'Government & Civic',
                'location': 'NorthSide Regeneration — Jefferson & Cass Ave',
                'city': 'St. Louis',
                'state': 'MO',
                'description': (
                    'The National Geospatial-Intelligence Agency\'s $1.75 billion campus consolidates '
                    '3,100 jobs and 3 million square feet of federal workspace in north St. Louis — '
                    'the largest federal construction project in Missouri history. Breaking ground in 2019, '
                    'the campus is reshaping the NorthSide with new infrastructure, transit improvements, '
                    'and workforce development partnerships with local trade unions.'
                ),
                'contractor': 'Clark Construction Group',
                'owner': 'U.S. National Geospatial-Intelligence Agency',
                'status': 'active',
                'start_date': datetime.date(2019, 9, 1),
                'estimated_cost': 1750000000,
                'featured': True,
            },
            {
                'title': 'MLS Stadium — St. Louis City SC Gateway to the Parks',
                'slug': 'mls-stl-city-sc-stadium',
                'category': 'Sports & Entertainment',
                'location': '100 Salvation Army Dr, Laclede\'s Landing',
                'city': 'St. Louis',
                'state': 'MO',
                'description': (
                    'The first purpose-built MLS stadium in Missouri, home of St. Louis City SC, '
                    'opened March 2023. The $459 million facility seats 22,500 and features a '
                    'dramatic canopy roof and a glass facade offering views of the Gateway Arch — '
                    'continuing St. Louis\'s tradition of architecture that honors its skyline landmark.'
                ),
                'contractor': 'Turner Construction',
                'owner': 'St. Louis City SC / Taylor family',
                'status': 'completed',
                'start_date': datetime.date(2021, 2, 15),
                'end_date': datetime.date(2023, 3, 2),
                'estimated_cost': 459000000,
                'featured': True,
            },
            {
                'title': 'Kansas City International Airport — New Single-Terminal',
                'slug': 'kci-new-terminal',
                'category': 'Infrastructure & Bridges',
                'location': 'KCI Airport, Kansas City, MO',
                'city': 'Kansas City',
                'state': 'MO',
                'description': (
                    'After decades of debate, Kansas City replaced its three-terminal 1970s airport '
                    'with a modern 1 million square foot single terminal. The $1.5 billion project '
                    'opened February 2023, featuring 39 gates, a 6,800-car parking garage, and '
                    'the largest airport construction project in Missouri history.'
                ),
                'contractor': 'Edgemoor Infrastructure & Real Estate / Turner Construction',
                'owner': 'City of Kansas City',
                'status': 'completed',
                'start_date': datetime.date(2019, 5, 28),
                'end_date': datetime.date(2023, 2, 28),
                'estimated_cost': 1500000000,
                'featured': True,
            },
            {
                'title': 'Centene Corporation HQ Expansion — Clayton',
                'slug': 'centene-hq-clayton',
                'category': 'Commercial Development',
                'location': '7700 Forsyth Blvd, Clayton, MO',
                'city': 'Clayton',
                'state': 'MO',
                'description': (
                    'One of Missouri\'s largest private employers expanded its Clayton headquarters '
                    'with twin 18-story towers adding 1.1 million square feet of office space, '
                    'connecting to a new parking structure and conference center. '
                    'The project created 2,000 construction jobs with significant IBEW and '
                    'Carpenters union participation.'
                ),
                'contractor': 'McCarthy Building Companies',
                'owner': 'Centene Corporation',
                'status': 'completed',
                'start_date': datetime.date(2018, 8, 1),
                'end_date': datetime.date(2021, 11, 1),
                'estimated_cost': 675000000,
                'featured': False,
            },
            {
                'title': 'I-270/I-255 Interchange Reconstruction',
                'slug': 'i270-i255-interchange',
                'category': 'Infrastructure & Bridges',
                'location': 'I-270 & I-255, South County St. Louis',
                'city': 'St. Louis',
                'state': 'MO',
                'description': (
                    'MoDOT\'s reconstruction of one of the St. Louis metro\'s most congested '
                    'interchanges, adding directional ramps, new pavement, and improved sightlines. '
                    'The project affects 100,000 daily commuters and involves coordination with '
                    'multiple IBEW and Operating Engineers union crews across 36 months of active construction.'
                ),
                'contractor': 'Millstone Weber',
                'owner': 'Missouri Department of Transportation',
                'status': 'active',
                'start_date': datetime.date(2023, 4, 3),
                'estimated_cost': 200000000,
                'featured': False,
            },
            {
                'title': 'SSM Health St. Louis University Hospital Tower Expansion',
                'slug': 'ssmh-slu-hospital-tower',
                'category': 'Healthcare',
                'location': '1201 S Grand Blvd, St. Louis, MO',
                'city': 'St. Louis',
                'state': 'MO',
                'description': (
                    'An 8-story patient tower adding 180 private rooms and expanding surgical '
                    'and ICU capacity at one of Missouri\'s flagship academic medical centers. '
                    'The $400M expansion employs over 800 union tradespeople across iron, electrical, '
                    'plumbing, and mechanical trades.'
                ),
                'contractor': 'Alberici Constructors',
                'owner': 'SSM Health / Saint Louis University',
                'status': 'active',
                'start_date': datetime.date(2022, 9, 1),
                'estimated_cost': 400000000,
                'featured': False,
            },
            {
                'title': 'Hawthorn Hill — Kansas City Affordable Housing',
                'slug': 'hawthorn-hill-kc',
                'category': 'Residential Development',
                'location': 'Prospect Corridor, Kansas City, MO',
                'city': 'Kansas City',
                'state': 'MO',
                'description': (
                    '180-unit mixed-income residential development anchoring the revitalization '
                    'of the Prospect Corridor, Kansas City\'s most ambitious housing initiative. '
                    'The project pairs Carpenters and Laborers union workforce with Section 8 '
                    'housing voucher recipients and first-time homebuyer units.'
                ),
                'contractor': 'Sunflower Development Group',
                'owner': 'Kansas City Housing Authority',
                'status': 'planning',
                'start_date': datetime.date(2026, 6, 1),
                'estimated_cost': 45000000,
                'featured': False,
            },
            {
                'title': 'WildCare Park — St. Louis Zoo North County Expansion',
                'slug': 'wildcare-park-stl-zoo',
                'category': 'Conservation & Wildlife',
                'location': 'Former Norwood Hills Country Club, 4301 Ashby Rd',
                'city': 'Normandy',
                'state': 'MO',
                'description': (
                    'The St. Louis Zoo\'s most ambitious expansion in a generation, WildCare Park '
                    'transforms the former Norwood Hills Country Club\'s 425-acre property in north '
                    'St. Louis County into a world-class wildlife conservation park.\n\n'
                    'The zoo-owned property — acquired after the golf club listed the land for sale — '
                    'is being developed to house large-habitat African and other exotic species in '
                    'naturalistic environments far exceeding what the Forest Park facility can provide. '
                    'The open-landscape design allows for vast roaming areas for hoofed animals, '
                    'replicating savanna conditions that standard zoo enclosures cannot achieve.\n\n'
                    'A drive-through experience component has been discussed in early planning documents, '
                    'which would make WildCare Park the first major American zoo facility to incorporate '
                    'a safari-style viewing format at this scale. The project represents a landmark '
                    'investment in north St. Louis County — a region that has historically been '
                    'underserved by major civic amenities — and is expected to generate significant '
                    'construction employment and long-term economic activity.\n\n'
                    'The St. Louis Zoo is one of the few free world-class zoos in the United States, '
                    'funded through a special tax district. WildCare Park extends that public mission '
                    'to a new geography and a new conservation model.'
                ),
                'owner': 'St. Louis Zoological Park',
                'status': 'planning',
                'start_date': datetime.date(2024, 1, 1),
                'estimated_cost': 130000000,
                'featured': True,
            },
            {
                'title': 'CityPark Active Transportation Network — 12-Direction Expansion',
                'slug': 'citypark-bike-network',
                'category': 'Infrastructure & Bridges',
                'location': 'CityPark Stadium — 100 Salvation Army Dr, expanding citywide',
                'city': 'St. Louis',
                'state': 'MO',
                'description': (
                    'St. Louis City SC and city planning partners are extending a comprehensive '
                    'network of protected bike lanes, multi-use paths, and pedestrian corridors '
                    'radiating outward from CityPark (Energizer Park) in 12 directions — '
                    'connecting the stadium to neighborhoods across north, south, east, and west '
                    'St. Louis and reaching as far as north St. Louis County.\n\n'
                    'The concept, sometimes described as a "clock face" network, treats the stadium '
                    'as a civic hub — not just a sports venue — and is designed to embed CityPark '
                    'into daily life for St. Louis residents by making it accessible on foot or by '
                    'bicycle from virtually every direction.\n\n'
                    'The project aligns with St. Louis City SC\'s stated commitment to urban '
                    'revitalization and complements the broader Gateway to the Parks initiative '
                    'that shaped the stadium\'s original development. The north-county corridor '
                    'connection would provide a direct active-transportation link toward the '
                    'WildCare Park development area — creating a potential spine connecting two of '
                    'the region\'s most significant new public amenities.'
                ),
                'owner': 'St. Louis City SC / City of St. Louis',
                'status': 'planning',
                'start_date': datetime.date(2025, 6, 1),
                'estimated_cost': 45000000,
                'featured': False,
            },
            {
                'title': 'One AT&T Center Redevelopment — Downtown St. Louis',
                'slug': 'att-building-downtown-stl',
                'category': 'Commercial Development',
                'location': '909 Chestnut St, Downtown St. Louis',
                'city': 'St. Louis',
                'state': 'MO',
                'description': (
                    'One AT&T Center — the 44-story tower that dominated the St. Louis skyline '
                    'for decades as the AT&T corporate headquarters — sat entirely vacant after '
                    'the telecommunications giant vacated the building, leaving the city\'s '
                    'second-tallest skyscraper as a hollow symbol of downtown disinvestment.\n\n'
                    'The property was acquired by a Boston-based developer for a reported $3.5 million '
                    '— a price that reflects both the enormous cost of renovation and the speculative '
                    'opportunity of bringing a landmark tower back to life. The redevelopment plan '
                    'calls for mixed-use conversion: market-rate apartments, condominiums, ground-floor '
                    'retail, and commercial office space.\n\n'
                    'To make the economics viable, developers are pursuing up to $300–350 million '
                    'in Tax Increment Financing (TIF) — among the largest TIF requests in St. Louis '
                    'history — from the city and state. TIF would fund the extraordinary structural '
                    'and systems work required to convert a 44-story 1980s office tower.\n\n'
                    'The building sits in near-direct sightline of the Gateway Mall — the one-mile '
                    'green corridor running west from the Gateway Arch past the Old Courthouse '
                    '(where the Dred Scott freedom case was heard), past the Veterans Memorial, '
                    'past Kiener Plaza, and toward Union Station. Activated residential floors '
                    'at this address would offer views that are essentially unmatched in Missouri.\n\n'
                    'If completed, the project would be the most significant single act of downtown '
                    'St. Louis revitalization in a generation.'
                ),
                'status': 'planning',
                'start_date': datetime.date(2025, 1, 1),
                'estimated_cost': 350000000,
                'featured': True,
            },
        ]

        for p in projects:
            cat_name = p.pop('category')
            if dry_run:
                self.stdout.write(f'  Would create: {p["title"]}')
            else:
                cat = cat_map.get(cat_name)
                project, created = Project.objects.get_or_create(
                    slug=p['slug'],
                    defaults={**p, 'category': cat},
                )
                verb = 'Created' if created else 'Exists'
                self.stdout.write(f'  {verb}: {project.title}')

        # ── Bid Opportunities ──────────────────────────────────────────────
        self.stdout.write('\n[6/6] Bid opportunities & permits')

        bids = [
            {
                'title': 'Gravois Road Bridge Deck Replacement',
                'agency': 'Missouri Department of Transportation',
                'city': 'St. Louis County',
                'state': 'MO',
                'description': 'Full-depth bridge deck replacement on Gravois Road over Meramec River. '
                               'DBE participation required at 15% minimum.',
                'status': 'open',
                'due_date': datetime.date(2026, 4, 15),
                'estimated_value': 4200000,
            },
            {
                'title': 'St. Louis Lambert Airport Terminal 1 Restroom Renovation',
                'agency': 'St. Louis Lambert International Airport',
                'city': 'St. Louis',
                'state': 'MO',
                'description': 'Renovation of 12 restroom suites in Terminal 1 concourses B and C. '
                               'Work must be phased to maintain terminal operations.',
                'status': 'open',
                'due_date': datetime.date(2026, 4, 22),
                'estimated_value': 3100000,
            },
            {
                'title': 'Kansas City Convention Center HVAC Replacement Phase III',
                'agency': 'Kansas City Facilities Management',
                'city': 'Kansas City',
                'state': 'MO',
                'description': 'Replacement of chiller plant and air handling units in halls D and E. '
                               'Sheet Metal Workers and Pipefitters certifications required.',
                'status': 'open',
                'due_date': datetime.date(2026, 5, 1),
                'estimated_value': 8750000,
            },
            {
                'title': 'St. Louis Public Schools Roof Replacement — 8 Buildings',
                'agency': 'St. Louis Public Schools',
                'city': 'St. Louis',
                'state': 'MO',
                'description': 'TPO membrane roofing replacement at 8 school buildings. '
                               'Prevailing wage project. Project labor agreement preferred.',
                'status': 'open',
                'due_date': datetime.date(2026, 5, 9),
                'estimated_value': 6400000,
            },
            {
                'title': 'Springfield Stormwater Outfall Improvements — Phase 2',
                'agency': 'City of Springfield Public Works',
                'city': 'Springfield',
                'state': 'MO',
                'description': 'Installation of 1,800 LF of 48-inch RCP storm sewer and related '
                               'surface improvements. Laborers and Operating Engineers prevailing wage.',
                'status': 'open',
                'due_date': datetime.date(2026, 5, 14),
                'estimated_value': 2900000,
            },
        ]

        for b in bids:
            if dry_run:
                self.stdout.write(f'  Would create bid: {b["title"]}')
            else:
                bid, created = BidOpportunity.objects.get_or_create(
                    title=b['title'],
                    defaults=b,
                )
                verb = 'Created' if created else 'Exists'
                self.stdout.write(f'  {verb}: {bid.title}')

        permits = [
            {
                'permit_number': 'STL-B-2026-00341',
                'permit_type': 'Commercial New Construction',
                'project_name': '4200 Olive St Mixed-Use Development',
                'address': '4200 Olive Blvd',
                'city': 'St. Louis',
                'state': 'MO',
                'contractor': 'Paric Corporation',
                'estimated_value': 18500000,
                'issued_date': datetime.date(2026, 3, 4),
                'status': 'active',
            },
            {
                'permit_number': 'STL-B-2026-00298',
                'permit_type': 'Interior Renovation',
                'project_name': 'Anheuser-Busch Brewery Visitor Center Renovation',
                'address': '1 Busch Place',
                'city': 'St. Louis',
                'state': 'MO',
                'contractor': 'Paric Corporation',
                'estimated_value': 4200000,
                'issued_date': datetime.date(2026, 2, 18),
                'status': 'active',
            },
            {
                'permit_number': 'CLAY-2026-00112',
                'permit_type': 'Commercial Addition',
                'project_name': 'Centene Campus Connector Bridge',
                'address': '7700 Forsyth Blvd',
                'city': 'Clayton',
                'state': 'MO',
                'contractor': 'McCarthy Building Companies',
                'estimated_value': 3100000,
                'issued_date': datetime.date(2026, 3, 10),
                'status': 'active',
            },
            {
                'permit_number': 'KC-COM-2026-01847',
                'permit_type': 'Commercial New Construction',
                'project_name': 'Crossroads Hotel Expansion — 9 Stories',
                'address': '2101 Central St',
                'city': 'Kansas City',
                'state': 'MO',
                'contractor': 'Ryan Companies US',
                'estimated_value': 32000000,
                'issued_date': datetime.date(2026, 3, 1),
                'status': 'active',
            },
            {
                'permit_number': 'SPFLD-2026-00487',
                'permit_type': 'Institutional New Construction',
                'project_name': 'Ozarks Technical Community College Health Sciences Building',
                'address': '1001 E Chestnut Expy',
                'city': 'Springfield',
                'state': 'MO',
                'contractor': 'Nabholz Construction',
                'estimated_value': 24500000,
                'issued_date': datetime.date(2026, 2, 25),
                'status': 'active',
            },
        ]

        for p in permits:
            if dry_run:
                self.stdout.write(f'  Would create permit: {p["permit_number"]}')
            else:
                permit_number = p['permit_number']
                permit_defaults = {k: v for k, v in p.items() if k not in ('permit_number', 'project_name')}
                # Prepend project_name to description so it isn't lost
                project_name = p.get('project_name', '')
                if project_name:
                    permit_defaults['description'] = f'{project_name}. {permit_defaults.get("description", "")}'.strip('. ')
                permit, created = PermitRecord.objects.get_or_create(
                    permit_number=permit_number,
                    defaults=permit_defaults,
                )
                verb = 'Created' if created else 'Exists'
                self.stdout.write(f'  {verb}: {permit.permit_number}')

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write('\n' + '=' * 72)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN complete. Run without --dry-run to save.'))
        else:
            self.stdout.write(self.style.SUCCESS('All content seeded successfully.'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('  1. Upload Busch Stadium III photos via admin:')
            self.stdout.write('     /admin/construction/galleryimage/add/')
            self.stdout.write('  2. Set SITE_MODE=construction in Azure App Settings')
            self.stdout.write('  3. Run: python manage.py collectstatic --noinput')
            self.stdout.write('  4. Deploy to Azure: az webapp deploy ...')
        self.stdout.write('=' * 72)
