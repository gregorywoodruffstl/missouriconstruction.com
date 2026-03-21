"""
management command: seed_stl_conversions
Creates seed data for the St. Louis Building Conversion Analysis feature.
Buildings sourced from public SLDC records, STLToday reporting, and permit archives.

Usage:
    python manage.py seed_stl_conversions
    python manage.py seed_stl_conversions --clear   (wipe and re-seed)
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from construction.models import (
    Neighborhood, TIFDistrict, BuildingConversion, ConversionFinancials
)


NEIGHBORHOODS = [
    {
        'name': 'Downtown St. Louis',
        'slug': 'downtown-st-louis',
        'district': 'downtown',
        'description': (
            'The historic core of St. Louis — bounded by the Gateway Arch, '
            'Busch Stadium, and the Arch grounds. Heavy concentration of hotel-to-residential '
            'conversions along Washington Avenue.'
        ),
        'latitude': 38.6270,
        'longitude': -90.1994,
        'walk_score': 92,
        'transit_score': 75,
        'crime_index': 210.0,
        'nearby_universities': ['SLU', 'Harris-Stowe State'],
        'nearby_hospitals': ['SSM Health St. Mary\'s', 'St. Louis University Hospital'],
        'grocery_stores': ['Schnucks', 'Whole Foods (nearby)'],
    },
    {
        'name': 'Midtown / Grand Center',
        'slug': 'midtown-grand-center',
        'district': 'midtown',
        'description': (
            'St. Louis\'s arts and entertainment corridor. Home to Fox Theatre, '
            'Powell Symphony Hall, and SLU campus. Growing residential base driven by '
            'university proximity and cultural investment.'
        ),
        'latitude': 38.6370,
        'longitude': -90.2220,
        'walk_score': 78,
        'transit_score': 62,
        'crime_index': 160.0,
        'nearby_universities': ['Saint Louis University', 'Harris-Stowe State'],
        'nearby_hospitals': ['SSM Health Saint Louis University Hospital'],
        'grocery_stores': ['Ruler Foods', 'Schnucks Midtown'],
    },
    {
        'name': 'Central West End',
        'slug': 'central-west-end',
        'district': 'central_west_end',
        'description': (
            'One of St. Louis\'s most walkable neighborhoods. Boutique retail, '
            'restaurant row, and the Forest Park gateway. Condo market anchored by '
            'medical professionals from BJC and WashU Medical.'
        ),
        'latitude': 38.6430,
        'longitude': -90.2640,
        'walk_score': 88,
        'transit_score': 58,
        'crime_index': 115.0,
        'nearby_universities': ['Washington University in St. Louis', 'Saint Louis University'],
        'nearby_hospitals': ['Barnes-Jewish Hospital', 'St. Louis Children\'s Hospital',
                             'Washington University Medical Center'],
        'grocery_stores': ['Straub\'s', 'Whole Foods Market'],
    },
    {
        'name': 'Lafayette Square',
        'slug': 'lafayette-square',
        'district': 'lafayette_sq',
        'description': (
            'Historic Victorian neighborhood surrounding Lafayette Park — '
            'St. Louis\'s oldest park. Known for restored mansions and brownstones. '
            'Millennial and young professional demographic.'
        ),
        'latitude': 38.6157,
        'longitude': -90.2210,
        'walk_score': 74,
        'transit_score': 50,
        'crime_index': 130.0,
        'nearby_universities': ['SLU (nearby)'],
        'nearby_hospitals': ['SSM Health'],
        'grocery_stores': ['Schnucks', 'Local co-op'],
    },
]

TIF_DISTRICTS = [
    {
        'name': 'Washington Avenue TIF District',
        'district_number': 'WA-001',
        'total_amount': 30_000_000.00,
        'term_years': 23,
        'sldc_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        'notes': 'Covers Washington Ave hotel conversion corridor, established early 2000s.',
    },
    {
        'name': 'Downtown St. Louis TIF #3',
        'district_number': 'DT-003',
        'total_amount': 52_000_000.00,
        'term_years': 23,
        'sldc_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        'notes': 'Broader downtown residential incentive zone.',
    },
    {
        'name': 'Grand Center TIF District',
        'district_number': 'GC-001',
        'total_amount': 18_500_000.00,
        'term_years': 23,
        'sldc_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        'notes': 'Arts and entertainment district TIF tied to Fox Theatre redevelopment zone.',
    },
]

CONVERSIONS = [
    # -------------------------------------------------------------------------
    # Washington Avenue Corridor — Hotel to Loft Boom (2000s–2010s)
    # -------------------------------------------------------------------------
    {
        'building': {
            'name': 'Roberts Tower → Roberts Mayfair Apartments',
            'original_name': 'Roberts Mayfair Hotel',
            'current_name': 'Roberts Mayfair Apartments',
            'address': '806 St. Charles St, St. Louis, MO 63101',
            'neighborhood_slug': 'downtown-st-louis',
            'tif_district_name': 'Washington Avenue TIF District',
            'original_building_type': 'hotel',
            'conversion_type': 'residential',
            'status': 'completed',
            'original_units': 182,
            'original_unit_label': 'hotel rooms',
            'year_built': 1925,
            'residential_units': 149,
            'unit_type': 'apartment',
            'completion_year': 2014,
            'description': (
                'The Roberts Mayfair, a grand 1925 hotel that hosted presidents and '
                'celebrities, sat vacant for years before conversion. Roberts Brothers '
                'Companies redeveloped the property into 149 market-rate apartments '
                'preserving the original Beaux-Arts lobby. Historic tax credits and '
                'TIF financing made the project financially viable after two failed '
                'prior attempts at redevelopment.'
            ),
            'developer': 'Roberts Brothers Companies',
            'architect': 'Mackey Mitchell Architects',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 4_200_000.00,
            'purchase_year': 2011,
            'rehab_cost_estimate': 28_000_000.00,
            'total_project_cost': 32_200_000.00,
            'tif_amount': 4_800_000.00,
            'historic_tax_credits': 7_200_000.00,
            'avg_rent_monthly': 1_450.00,
            'avg_hoa_monthly': None,
            'data_confidence': 'medium',
            'data_sources': 'STLToday, SLDC project database, Missouri DHCD historic credits',
        },
    },
    {
        'building': {
            'name': 'Ambassador Hotel → Ambassador Apartments',
            'original_name': 'Hotel Ambassador',
            'current_name': 'Ambassador Apartments',
            'address': '1820 Chestnut Pl, St. Louis, MO 63103',
            'neighborhood_slug': 'downtown-st-louis',
            'tif_district_name': 'Washington Avenue TIF District',
            'original_building_type': 'hotel',
            'conversion_type': 'residential',
            'status': 'completed',
            'original_units': 285,
            'original_unit_label': 'hotel rooms',
            'year_built': 1921,
            'residential_units': 205,
            'unit_type': 'mixed',
            'completion_year': 2009,
            'description': (
                'The 1921 Ambassador Hotel on Chestnut was a cornerstone of St. Louis '
                'hospitality for decades. After decades of vacancy, it was among the '
                'first major Washington Avenue corridor hotel conversions, setting the '
                'template for subsequent adaptive reuse projects downtown.'
            ),
            'developer': 'Pyramid Construction',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 3_100_000.00,
            'purchase_year': 2006,
            'rehab_cost_estimate': 22_500_000.00,
            'total_project_cost': 25_600_000.00,
            'tif_amount': 5_100_000.00,
            'historic_tax_credits': 6_000_000.00,
            'avg_rent_monthly': 1_295.00,
            'data_confidence': 'medium',
            'data_sources': 'SLDC, STLToday archive, Missouri historic credits database',
        },
    },
    {
        'building': {
            'name': 'Railway Exchange Building → Residences at Railway Exchange',
            'original_name': 'Railway Exchange Building',
            'current_name': 'Residences at Railway Exchange',
            'address': '611 Olive St, St. Louis, MO 63101',
            'neighborhood_slug': 'downtown-st-louis',
            'tif_district_name': 'Downtown St. Louis TIF #3',
            'original_building_type': 'office',
            'conversion_type': 'mixed_residential',
            'status': 'in_progress',
            'original_units': 1_400_000,
            'original_unit_label': 'sq ft',
            'year_built': 1913,
            'residential_units': 300,
            'unit_type': 'mixed',
            'completion_year': 2026,
            'description': (
                'One of the most significant adaptive reuse projects in St. Louis history. '
                'The 21-story Railway Exchange Building — once home to Famous-Barr department '
                'store and anchoring 600K sqft of St. Louis retail — is being converted into '
                'mixed-income residential with ground-floor commercial. A $300M+ project '
                'backed by historic tax credits, NMTC, and city TIF financing.'
            ),
            'developer': 'Restoration St. Louis / WRG Development',
            'architect': 'Arcturis',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 24_000_000.00,
            'purchase_year': 2022,
            'total_project_cost': 325_000_000.00,
            'tif_amount': 36_000_000.00,
            'historic_tax_credits': 82_000_000.00,
            'nmtc_amount': 12_000_000.00,
            'avg_rent_monthly': 1_800.00,
            'data_confidence': 'medium',
            'data_sources': 'STLToday, SLDC, Missouri Historic Preservation Office, city press releases',
        },
    },
    {
        'building': {
            'name': 'Syndicate Trust Building → Syndicate Residential',
            'original_name': 'Syndicate Trust Building',
            'current_name': 'Syndicate Residential',
            'address': '915 Olive St, St. Louis, MO 63101',
            'neighborhood_slug': 'downtown-st-louis',
            'tif_district_name': 'Downtown St. Louis TIF #3',
            'original_building_type': 'bank',
            'conversion_type': 'residential',
            'status': 'completed',
            'original_units': 18,
            'original_unit_label': 'floors',
            'year_built': 1907,
            'residential_units': 130,
            'unit_type': 'apartment',
            'completion_year': 2016,
            'description': (
                'The iconic Syndicate Trust Building — a Beaux-Arts tower at 9th and Olive '
                'with its famous clock — was converted to 130 market-rate apartments. '
                'One of St. Louis\'s most recognizable facades. The conversion preserved '
                'the original banking hall as a leasing office and community space.'
            ),
            'developer': 'Lawrence Group',
            'architect': 'Lawrence Group',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 5_500_000.00,
            'purchase_year': 2013,
            'rehab_cost_estimate': 19_000_000.00,
            'total_project_cost': 24_500_000.00,
            'tif_amount': 3_200_000.00,
            'historic_tax_credits': 5_800_000.00,
            'avg_rent_monthly': 1_550.00,
            'avg_hoa_monthly': None,
            'data_confidence': 'medium',
            'data_sources': 'SLDC, STLToday, Lawrence Group press releases',
        },
    },
    # -------------------------------------------------------------------------
    # Midtown / Grand Center
    # -------------------------------------------------------------------------
    {
        'building': {
            'name': 'Mercantile Library Tower → Lofts at Grand',
            'original_name': 'National City Bank Building / Mercantile Tower',
            'current_name': 'Lofts at Grand',
            'address': '3615 Olive St, St. Louis, MO 63108',
            'neighborhood_slug': 'midtown-grand-center',
            'tif_district_name': 'Grand Center TIF District',
            'original_building_type': 'office',
            'conversion_type': 'residential',
            'status': 'completed',
            'original_units': 12,
            'original_unit_label': 'floors',
            'year_built': 1927,
            'residential_units': 72,
            'unit_type': 'apartment',
            'completion_year': 2008,
            'description': (
                'Midtown adaptive reuse adjacent to the Fox Theatre. The 12-story office '
                'building was converted to 72 loft apartments as part of the Grand Center '
                'arts district revitalization. Strong student and arts-community tenant base '
                'given proximity to SLU and Saint Louis Conservatory.'
            ),
            'developer': 'Grand Center Inc.',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 1_800_000.00,
            'purchase_year': 2005,
            'rehab_cost_estimate': 9_500_000.00,
            'total_project_cost': 11_300_000.00,
            'tif_amount': 2_100_000.00,
            'historic_tax_credits': 2_800_000.00,
            'avg_rent_monthly': 1_150.00,
            'data_confidence': 'medium',
            'data_sources': 'SLDC, Grand Center Inc. annual reports, STLToday',
        },
    },
    # -------------------------------------------------------------------------
    # Central West End / BJC Corridor
    # -------------------------------------------------------------------------
    {
        'building': {
            'name': 'Forest Park Hotel → Park Place Condominiums',
            'original_name': 'Forest Park Hotel',
            'current_name': 'Park Place Condominiums',
            'address': '4630 Lindell Blvd, St. Louis, MO 63108',
            'neighborhood_slug': 'central-west-end',
            'tif_district_name': None,
            'original_building_type': 'hotel',
            'conversion_type': 'residential',
            'status': 'completed',
            'original_units': 220,
            'original_unit_label': 'hotel rooms',
            'year_built': 1929,
            'residential_units': 142,
            'unit_type': 'condo',
            'completion_year': 2004,
            'description': (
                'A Lindell Boulevard landmark reborn as upscale condominiums. The Forest Park '
                'Hotel\'s conversion was an early proof-of-concept for CWE residential density. '
                'Prime location one block from Forest Park and walking distance to the BJC '
                'medical campus makes this a perennial draw for physicians and WashU residents.'
            ),
            'developer': 'McBride & Son Homes',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 6_200_000.00,
            'purchase_year': 2001,
            'rehab_cost_estimate': 18_000_000.00,
            'total_project_cost': 24_200_000.00,
            'avg_sale_price': 285_000.00,
            'avg_hoa_monthly': 425.00,
            'avg_property_tax_annual': 3_800.00,
            'data_confidence': 'medium',
            'data_sources': 'STLToday, St. Louis City Assessor records, McBride press releases',
        },
    },
    # -------------------------------------------------------------------------
    # Washington Avenue Warehouse District
    # -------------------------------------------------------------------------
    {
        'building': {
            'name': 'Shoe District Warehouse → Washington Avenue Lofts',
            'original_name': 'Brown Shoe Company Warehouse Block',
            'current_name': 'Washington Avenue Lofts',
            'address': '1027 Washington Ave, St. Louis, MO 63101',
            'neighborhood_slug': 'downtown-st-louis',
            'tif_district_name': 'Washington Avenue TIF District',
            'original_building_type': 'warehouse',
            'conversion_type': 'residential',
            'status': 'completed',
            'original_units': 280_000,
            'original_unit_label': 'sq ft',
            'year_built': 1904,
            'residential_units': 189,
            'unit_type': 'apartment',
            'completion_year': 2003,
            'description': (
                'Part of the Washington Avenue "Shoe District" — St. Louis was once the '
                'shoe capital of America and the warehouses that stored inventory became '
                'the backbone of downtown residential revival. This block was among the '
                'first wave of warehouse-to-loft conversions that sparked the Washington '
                'Avenue transformation in the early 2000s.'
            ),
            'developer': 'Pyramid Construction',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 2_400_000.00,
            'purchase_year': 2000,
            'rehab_cost_estimate': 14_200_000.00,
            'total_project_cost': 16_600_000.00,
            'tif_amount': 3_800_000.00,
            'historic_tax_credits': 4_100_000.00,
            'avg_rent_monthly': 1_100.00,
            'data_confidence': 'medium',
            'data_sources': 'SLDC, STLToday, Washington Avenue Business Association',
        },
    },
    # -------------------------------------------------------------------------
    # Lafayette Square
    # -------------------------------------------------------------------------
    {
        'building': {
            'name': 'Lafayette Building → Lafayette Square Condominiums',
            'original_name': 'Lafayette Building (Commercial)',
            'current_name': 'Lafayette Square Condominiums',
            'address': '2001 Park Ave, St. Louis, MO 63104',
            'neighborhood_slug': 'lafayette-square',
            'tif_district_name': None,
            'original_building_type': 'mixed',
            'conversion_type': 'residential',
            'status': 'completed',
            'original_units': 8,
            'original_unit_label': 'floors',
            'year_built': 1910,
            'residential_units': 48,
            'unit_type': 'condo',
            'completion_year': 2007,
            'description': (
                'Lafayette Square\'s most prominent mixed-use adaptive reuse. The building '
                'overlooks Lafayette Park — the oldest public park in St. Louis — and '
                'attracted buyers seeking the walkable, historic character of one of '
                'St. Louis\'s most photographed neighborhoods.'
            ),
            'developer': 'Integrity Homes',
            'source_url': 'https://www.stlouis-mo.gov/government/departments/sldc/',
        },
        'financials': {
            'purchase_price': 1_200_000.00,
            'purchase_year': 2004,
            'rehab_cost_estimate': 7_800_000.00,
            'total_project_cost': 9_000_000.00,
            'historic_tax_credits': 2_200_000.00,
            'avg_sale_price': 195_000.00,
            'avg_hoa_monthly': 285.00,
            'data_confidence': 'estimate',
            'data_sources': 'STLToday, City Assessor, neighborhood association records',
        },
    },
]


class Command(BaseCommand):
    help = 'Seed STL Building Conversion Analysis data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing conversion data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            ConversionFinancials.objects.all().delete()
            BuildingConversion.objects.all().delete()
            TIFDistrict.objects.all().delete()
            Neighborhood.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all conversion data.'))

        # Seed Neighborhoods
        nbhd_map = {}
        for n in NEIGHBORHOODS:
            obj, created = Neighborhood.objects.update_or_create(
                slug=n['slug'],
                defaults={k: v for k, v in n.items() if k != 'slug'},
            )
            nbhd_map[n['slug']] = obj
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status} neighborhood: {obj.name}')

        # Seed TIF Districts
        tif_map = {}
        for t in TIF_DISTRICTS:
            obj, created = TIFDistrict.objects.update_or_create(
                name=t['name'],
                defaults={k: v for k, v in t.items() if k != 'name'},
            )
            tif_map[t['name']] = obj
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status} TIF district: {obj.name}')

        # Seed Buildings + Financials
        for item in CONVERSIONS:
            b = item['building']
            f = item.get('financials', {})

            neighborhood = nbhd_map.get(b.pop('neighborhood_slug'))
            tif_name = b.pop('tif_district_name', None)
            tif_district = tif_map.get(tif_name) if tif_name else None

            slug = slugify(b['name'])
            building, created = BuildingConversion.objects.update_or_create(
                slug=slug,
                defaults={
                    **b,
                    'neighborhood': neighborhood,
                    'tif_district': tif_district,
                    'featured': True,
                    'published': True,
                },
            )

            if f:
                ConversionFinancials.objects.update_or_create(
                    building=building,
                    defaults=f,
                )

            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'  {status}: {building.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeded {len(NEIGHBORHOODS)} neighborhoods, '
            f'{len(TIF_DISTRICTS)} TIF districts, '
            f'{len(CONVERSIONS)} building conversions.\n'
            f'   View at: /stl-conversions/'
        ))
