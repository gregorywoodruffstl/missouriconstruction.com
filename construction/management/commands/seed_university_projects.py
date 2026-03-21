"""
Seed University Construction Projects — UMSL + SLU
====================================================
Adds notable construction projects from:
  - University of Missouri - St. Louis (UMSL) — Gregory Woodruff's alma mater (undergrad)
  - Saint Louis University (SLU) — Gregory Woodruff's MBA

Both are large St. Louis institutions with active Facebook/LinkedIn alumni groups,
giving missouriconstruction.com strong social sharing opportunities.

Usage:
    python manage.py seed_university_projects
    python manage.py seed_university_projects --dry-run
    python manage.py seed_university_projects --university umsl
    python manage.py seed_university_projects --university slu
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Seed UMSL and SLU construction projects into Missouri Construction database'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Print what would be created without saving')
        parser.add_argument(
            '--university',
            choices=['umsl', 'slu', 'both'],
            default='both',
            help='Which university to seed (default: both)',
        )

    def handle(self, *args, **options):
        from construction.models import Project, ProjectCategory

        dry_run = options['dry_run']
        university = options['university']

        self.stdout.write(self.style.HTTP_REDIRECT('SEED UNIVERSITY PROJECTS — UMSL + SLU'))
        self.stdout.write('=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — nothing will be saved'))

        # Ensure required categories exist
        category_map = {}
        for cat_name, cat_slug in [
            ('Higher Education', 'higher-education'),
            ('Sports & Recreation', 'sports-recreation'),
            ('Healthcare', 'healthcare'),
            ('Research & Science', 'research-science'),
            ('Student Housing', 'student-housing'),
        ]:
            if not dry_run:
                cat, created = ProjectCategory.objects.get_or_create(
                    slug=cat_slug,
                    defaults={'name': cat_name, 'order': 10}
                )
                category_map[cat_slug] = cat
                if created:
                    self.stdout.write(f'  + Category: {cat_name}')
            else:
                self.stdout.write(f'  [DRY] Category: {cat_name}')

        created_count = 0

        # ─────────────────────────────────────────────
        # UMSL PROJECTS
        # ─────────────────────────────────────────────
        if university in ('umsl', 'both'):
            self.stdout.write(self.style.SUCCESS('\n📚 UNIVERSITY OF MISSOURI – ST. LOUIS (UMSL)'))
            self.stdout.write('Gregory Woodruff\'s undergraduate alma mater')
            self.stdout.write('-' * 50)

            umsl_projects = [
                {
                    'title': 'UMSL Millennium Student Center Renovation',
                    'category_slug': 'higher-education',
                    'location': '1 University Blvd',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Major renovation and expansion of the Millennium Student Center, the hub of student activity '
                        'at the University of Missouri–St. Louis. The project modernized dining facilities, created '
                        'flexible event spaces, upgraded technology infrastructure, and improved accessibility '
                        'throughout the building. UMSL serves over 16,000 students on its north St. Louis County campus.'
                    ),
                    'contractor': 'Paric Corporation',
                    'owner': 'University of Missouri–St. Louis',
                    'architect': 'Mackey Mitchell Architects',
                    'status': 'completed',
                    'start_date': date(2019, 6, 1),
                    'end_date': date(2021, 8, 15),
                    'estimated_cost': Decimal('24500000'),
                    'featured': True,
                },
                {
                    'title': 'UMSL Science Learning Center',
                    'category_slug': 'research-science',
                    'location': '1 University Blvd — North Campus',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Construction of a new state-of-the-art Science Learning Center consolidating UMSL\'s '
                        'biology, chemistry, and physics teaching labs into a single modern facility. '
                        'The building features collaborative learning studios, a research greenhouse, and '
                        'a rooftop observation deck. Designed to support UMSL\'s growing STEM enrollment '
                        'and the university\'s strategic plan for research excellence in the St. Louis region.'
                    ),
                    'contractor': 'S. M. Wilson & Co.',
                    'owner': 'University of Missouri–St. Louis / UM System',
                    'architect': 'HOK (Hellmuth, Obata + Kassabaum)',
                    'status': 'completed',
                    'start_date': date(2015, 3, 1),
                    'end_date': date(2017, 8, 20),
                    'estimated_cost': Decimal('52000000'),
                    'featured': True,
                },
                {
                    'title': 'UMSL RecPlex Aquatic Center Expansion',
                    'category_slug': 'sports-recreation',
                    'location': '131 Natural Bridge Road',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Expansion and modernization of the Mark Twain Athletic and Recreation Complex at UMSL. '
                        'Project included a new competition pool meeting NCAA standards, updated fitness center '
                        'equipment, improved locker facilities, and a new athletic training suite. '
                        'The expansion supports UMSL\'s Division II athletic programs and serves the broader '
                        'north St. Louis County community through community membership programs.'
                    ),
                    'contractor': 'Alberici Constructors',
                    'owner': 'University of Missouri–St. Louis',
                    'architect': 'Farnsworth Group',
                    'status': 'completed',
                    'start_date': date(2018, 9, 15),
                    'end_date': date(2020, 5, 1),
                    'estimated_cost': Decimal('18700000'),
                    'featured': False,
                },
                {
                    'title': 'UMSL Touhill Performing Arts Center Plaza',
                    'category_slug': 'higher-education',
                    'location': '1 University Blvd — MSC Campus',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Renovation of the outdoor plaza and public entrance to the Blanche M. Touhill '
                        'Performing Arts Center, a world-class concert and event venue on the UMSL campus. '
                        'The Touhill hosts the St. Louis Symphony Orchestra, Broadway touring productions, '
                        'and major community events for north St. Louis County. Project included new hardscape, '
                        'accessible pathways, updated exterior lighting, and improved parking access.'
                    ),
                    'contractor': 'KCI Construction',
                    'owner': 'University of Missouri–St. Louis Foundation',
                    'architect': 'Cannon Design',
                    'status': 'completed',
                    'start_date': date(2022, 4, 1),
                    'end_date': date(2023, 3, 30),
                    'estimated_cost': Decimal('4200000'),
                    'featured': False,
                },
            ]

            for proj_data in umsl_projects:
                slug = slugify(proj_data['title'])
                if Project.objects.filter(slug=slug).exists():
                    self.stdout.write(f'  ⚠ SKIP (exists): {proj_data["title"]}')
                    continue
                if dry_run:
                    self.stdout.write(f'  [DRY] Would create: {proj_data["title"]} (${proj_data["estimated_cost"]:,.0f})')
                    continue
                cat = category_map.get(proj_data.pop('category_slug'))
                Project.objects.create(
                    **proj_data,
                    category=cat,
                    slug=slug,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {proj_data["title"]}'))

        # ─────────────────────────────────────────────
        # SLU PROJECTS
        # ─────────────────────────────────────────────
        if university in ('slu', 'both'):
            self.stdout.write(self.style.SUCCESS('\n🎓 SAINT LOUIS UNIVERSITY (SLU)'))
            self.stdout.write('Gregory Woodruff\'s MBA alma mater')
            self.stdout.write('-' * 50)

            slu_projects = [
                {
                    'title': 'SLU Chaifetz Arena',
                    'category_slug': 'sports-recreation',
                    'location': '1 S Compton Ave',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Construction of the Chaifetz Arena, a premier 10,600-seat multi-purpose entertainment '
                        'and sports venue on the Saint Louis University campus. The arena serves as home court '
                        'for the SLU Billikens men\'s and women\'s basketball teams and hosts major concerts, '
                        'family shows, and community events. Located at the edge of SLU\'s midtown St. Louis '
                        'campus, the arena has become an anchor for the Grand Center arts and entertainment district. '
                        'The project won multiple design and construction awards.'
                    ),
                    'contractor': 'McCarthy Building Companies',
                    'owner': 'Saint Louis University',
                    'architect': 'Populous (formerly HOK Sport)',
                    'status': 'completed',
                    'start_date': date(2006, 3, 1),
                    'end_date': date(2008, 10, 1),
                    'estimated_cost': Decimal('80000000'),
                    'featured': True,
                },
                {
                    'title': 'SLU Laclede Hall Student Center Renovation',
                    'category_slug': 'higher-education',
                    'location': '221 N Grand Blvd',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Comprehensive renovation of Laclede Hall, the primary student services hub at Saint '
                        'Louis University. The project modernized student government offices, the financial aid '
                        'center, academic advising, and created new collaborative study environments. '
                        'Updated dining areas reflect SLU\'s Jesuit commitment to community and social justice. '
                        'Project used sustainable construction practices aligning with SLU\'s carbon-neutral goals.'
                    ),
                    'contractor': 'BSI Constructors',
                    'owner': 'Saint Louis University',
                    'architect': 'Mackey Mitchell Architects',
                    'status': 'completed',
                    'start_date': date(2020, 5, 15),
                    'end_date': date(2022, 1, 10),
                    'estimated_cost': Decimal('16800000'),
                    'featured': True,
                },
                {
                    'title': 'SLU School of Medicine — Doisy Research Center II',
                    'category_slug': 'research-science',
                    'location': '1100 S Grand Blvd',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Expansion of the Edward A. Doisy Research Center, a flagship biomedical research '
                        'facility at the SLU School of Medicine. Phase II added new laboratory floors for '
                        'cancer research, infectious disease studies, and molecular pharmacology. '
                        'The School of Medicine\'s research enterprise generates over $50 million annually '
                        'in sponsored research funding. The Doisy Research Center has been a cornerstone '
                        'of St. Louis\'s growing bioscience corridor alongside Washington University and Barnes-Jewish.'
                    ),
                    'contractor': 'Clayco Inc.',
                    'owner': 'Saint Louis University School of Medicine',
                    'architect': 'CannonDesign',
                    'status': 'completed',
                    'start_date': date(2017, 7, 1),
                    'end_date': date(2020, 2, 28),
                    'estimated_cost': Decimal('68000000'),
                    'featured': True,
                },
                {
                    'title': 'SLU Midtown Campus — Chouteau Greenway Gateway',
                    'category_slug': 'higher-education',
                    'location': 'Grand Blvd at Chouteau Ave',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Saint Louis University\'s contribution to the Chouteau Greenway project, a 6.5-mile '
                        'linear park and trail connecting Forest Park to the Mississippi River. SLU partnered '
                        'with Great Rivers Greenway to redesign the Grand Avenue campus gateway, creating an '
                        'urban plaza that links the university to the community trail system. The project '
                        'included new hardscape, bioswales, public art installations, and improved cyclist '
                        'and pedestrian safety at one of St. Louis\'s busiest intersections.'
                    ),
                    'contractor': 'KCI Construction',
                    'owner': 'Saint Louis University / Great Rivers Greenway',
                    'architect': 'Stoss Landscape Urbanism',
                    'status': 'completed',
                    'start_date': date(2023, 4, 1),
                    'end_date': date(2024, 11, 15),
                    'estimated_cost': Decimal('11500000'),
                    'featured': False,
                },
                {
                    'title': 'SLU Spring Hall Residence Hall',
                    'category_slug': 'student-housing',
                    'location': '3701 Laclede Ave',
                    'city': 'St. Louis',
                    'state': 'MO',
                    'description': (
                        'Construction of Spring Hall, a new residence hall housing 400 students in suite-style '
                        'accommodations. Spring Hall replaced aging dormitory space and added a first-floor '
                        'community lounge, maker space, and 24/7 study rooms. The building achieved LEED '
                        'Silver certification for its energy efficiency and use of recycled construction materials. '
                        'SLU\'s campus housing expansion is part of a strategic initiative to increase residential '
                        'student engagement and campus community.'
                    ),
                    'contractor': 'S. M. Wilson & Co.',
                    'owner': 'Saint Louis University',
                    'architect': 'Hastings+Chivetta Architects',
                    'status': 'completed',
                    'start_date': date(2021, 8, 1),
                    'end_date': date(2023, 7, 31),
                    'estimated_cost': Decimal('38000000'),
                    'featured': False,
                },
            ]

            for proj_data in slu_projects:
                slug = slugify(proj_data['title'])
                if Project.objects.filter(slug=slug).exists():
                    self.stdout.write(f'  ⚠ SKIP (exists): {proj_data["title"]}')
                    continue
                if dry_run:
                    self.stdout.write(f'  [DRY] Would create: {proj_data["title"]} (${proj_data["estimated_cost"]:,.0f})')
                    continue
                cat = category_map.get(proj_data.pop('category_slug'))
                Project.objects.create(
                    **proj_data,
                    category=cat,
                    slug=slug,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {proj_data["title"]}'))

        self.stdout.write('\n' + '=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN complete — run without --dry-run to save'))
        else:
            total = len(umsl_projects if university == 'umsl' else []) + \
                    len(slu_projects if university == 'slu' else []) + \
                    (len(umsl_projects) + len(slu_projects) if university == 'both' else 0)
            self.stdout.write(self.style.SUCCESS(
                f'✅ Done! Created {created_count} projects. '
                f'UMSL + SLU are now featured on missouriconstruction.com 🎓'
            ))
