"""
Seed Affiliate Partners — Missouri Construction
================================================
Populates the Affiliate table with construction industry affiliate programs:
  - Hand tools + power tools (Amazon Associates, Home Depot partner)
  - Software (Autodesk/AutoCAD, Bluebeam, STACK Estimating)
  - Safety & PPE (SafetyGear.com, Grainger)
  - Work apparel (Carhartt, Duluth Trading)
  - Equipment rental (Sunbelt Rentals)

All contractors, site supers, and project managers are the target audience.
Commission rates are indicative — enroll in each program to confirm current rates.

Usage:
    python manage.py seed_affiliates
    python manage.py seed_affiliates --dry-run
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed affiliate partner data for Missouri Construction'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        from construction.models import Affiliate

        dry_run = options['dry_run']
        self.stdout.write(self.style.HTTP_REDIRECT('SEED AFFILIATES — MISSOURI CONSTRUCTION'))
        self.stdout.write('=' * 60)

        affiliates = [

            # ── HAND TOOLS ──────────────────────────────────────────────
            {
                'name': 'Amazon Associates — Hand Tools',
                'category': 'hand_tools',
                'affiliate_url': 'https://www.amazon.com/s?k=hand+tools+construction&tag=YOUR_ASSOCIATE_TAG',
                'tagline': 'Millions of tools shipped to your job site',
                'description': (
                    'Amazon Associates gives Missouri Construction a commission on every tool purchased '
                    'through our links. From chisels to levels to tape measures — anything a contractor '
                    'needs is on Amazon with Prime 2-day shipping. '
                    'Sign up: https://affiliate-program.amazon.com/'
                ),
                'commission_rate': '3–8%',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/320px-Amazon_logo.svg.png',
                'featured': True,
                'order': 1,
            },
            {
                'name': 'Home Depot Pro — Hand Tools',
                'category': 'hand_tools',
                'affiliate_url': 'https://www.homedepot.com/b/Tools-Hand-Tools/N-5yc1vZc2bc?ref=YOUR_AFFILIATE_ID',
                'tagline': 'The contractor\'s choice — store & jobsite delivery',
                'description': (
                    'Home Depot\'s affiliate program through Impact Radius. '
                    'Strong with Missouri contractors who already have Pro accounts. '
                    'Sign up: https://www.impactradius.com/ — search "Home Depot"'
                ),
                'commission_rate': '2–4%',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/TheHomeDepot.svg/320px-TheHomeDepot.svg.png',
                'featured': True,
                'order': 2,
            },

            # ── POWER TOOLS ─────────────────────────────────────────────
            {
                'name': 'Milwaukee Tool — Amazon',
                'category': 'power_tools',
                'affiliate_url': 'https://www.amazon.com/stores/MilwaukeeTool/page/YOUR_TAG',
                'tagline': 'The brand every Missouri framer trusts',
                'description': (
                    'Milwaukee Tool is the #1 brand on construction sites in the Midwest. '
                    'Link directly to Milwaukee M18 drills, saws, and battery systems via Amazon Associates. '
                    'High AOV = strong commission dollars per transaction.'
                ),
                'commission_rate': '3–6% via Amazon',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Milwaukee_Tool_logo.svg/320px-Milwaukee_Tool_logo.svg.png',
                'featured': True,
                'order': 3,
            },
            {
                'name': 'DeWalt Tools — Amazon',
                'category': 'power_tools',
                'affiliate_url': 'https://www.amazon.com/stores/DEWALT/page/YOUR_TAG',
                'tagline': 'Trusted on every St. Louis job site',
                'description': (
                    'DeWalt 20V MAX and FLEXVOLT systems dominate commercial construction. '
                    'Average cart values are $200–$600 when professionals buy full kits.'
                ),
                'commission_rate': '3–6% via Amazon',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/DEWALT_logo.svg/320px-DEWALT_logo.svg.png',
                'featured': False,
                'order': 4,
            },

            # ── SOFTWARE ────────────────────────────────────────────────
            {
                'name': 'Autodesk AutoCAD',
                'category': 'software',
                'affiliate_url': 'https://www.autodesk.com/products/autocad/overview?mktvar002=YOUR_AFFILIATE_ID',
                'tagline': 'The industry standard for architecture & construction drawings',
                'description': (
                    'Autodesk runs one of the highest-paying B2B affiliate programs ($100–$250 per subscription). '
                    'AutoCAD LT starts at $60/month — architects, engineers, and contractors all need it. '
                    'Missouri Construction readers are exactly the right audience. '
                    'Sign up: https://www.autodesk.com/partners/affiliate-program'
                ),
                'commission_rate': '$100–$250 per new subscription',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Above_Gotham.svg/1200px-Above_Gotham.svg.png',
                'featured': True,
                'order': 5,
            },
            {
                'name': 'Bluebeam Revu',
                'category': 'software',
                'affiliate_url': 'https://www.bluebeam.com/solutions/revu/?ref=YOUR_AFFILIATE_ID',
                'tagline': 'PDF markup + plan management for construction teams',
                'description': (
                    'Bluebeam Revu is the go-to PDF collaboration tool for Missouri GCs and subs. '
                    'Project managers use it to mark up drawings, manage submittals, and track RFIs. '
                    'Bluebeam Basics starts at $240/year. $80+ commission per converted referral. '
                    'Sign up: https://www.bluebeam.com/partner-programs/'
                ),
                'commission_rate': '~$80/subscription',
                'logo_url': '',
                'featured': True,
                'order': 6,
            },
            {
                'name': 'STACK Estimating Software',
                'category': 'software',
                'affiliate_url': 'https://www.stackct.com/?ref=YOUR_AFFILIATE_ID',
                'tagline': 'Cloud-based takeoff and estimating for contractors',
                'description': (
                    'STACK is the leading cloud-based estimating and takeoff tool for commercial '
                    'and residential contractors. Replaces manual blueprint measuring with digital '
                    'takeoffs from PDF files. Start with a free trial — paid plans start at $2,499/year. '
                    'Sign up: https://www.stackct.com/affiliate-program'
                ),
                'commission_rate': '20% of first year subscription',
                'logo_url': '',
                'featured': False,
                'order': 7,
            },

            # ── SAFETY & PPE ─────────────────────────────────────────────
            {
                'name': 'Grainger — Safety & PPE',
                'category': 'safety',
                'affiliate_url': 'https://www.grainger.com/category/safety?ref=YOUR_AFFILIATE_ID',
                'tagline': 'Hard hats, gloves, harnesses — delivered next day',
                'description': (
                    'Grainger is the largest industrial supply distributor in North America. '
                    'Missouri contractors trust Grainger for hard hats (msa, MSA), safety glasses, '
                    'fall protection, and respirators. Grainger affiliate program via CJ Affiliate. '
                    'Sign up: https://www.cj.com/ — search "Grainger"'
                ),
                'commission_rate': '2–4%',
                'logo_url': '',
                'featured': True,
                'order': 8,
            },
            {
                'name': 'Amazon — OSHA Safety Equipment',
                'category': 'safety',
                'affiliate_url': 'https://www.amazon.com/s?k=OSHA+construction+safety+equipment&tag=YOUR_ASSOCIATE_TAG',
                'tagline': 'Keep your crew compliant and protected',
                'description': (
                    'From Class 2 safety vests to first aid kits to fire extinguishers — '
                    'Missouri job sites need OSHA-compliant safety equipment delivered fast. '
                    'Amazon Associates covers all safety gear with competitive commissions.'
                ),
                'commission_rate': '3–8% via Amazon',
                'logo_url': '',
                'featured': False,
                'order': 9,
            },

            # ── WORK APPAREL ─────────────────────────────────────────────
            {
                'name': 'Carhartt Work Apparel',
                'category': 'apparel',
                'affiliate_url': 'https://www.carhartt.com/?utm_source=affiliate&utm_campaign=YOUR_ID',
                'tagline': 'Built for Missouri winters on the job site',
                'description': (
                    'Carhartt is the iconic American workwear brand — duck canvas jackets, flannel-lined '
                    'bibs, and steel-toe boots that Missouri construction workers swear by. '
                    'Carhartt affiliate program available via CJ Affiliate or ShareASale. '
                    'Sign up: https://www.shareasale.com/ — search "Carhartt"'
                ),
                'commission_rate': '5–8%',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/36/Carhartt_wordmark.svg/320px-Carhartt_wordmark.svg.png',
                'featured': True,
                'order': 10,
            },
            {
                'name': 'Duluth Trading Co. — Work Pants & Gear',
                'category': 'apparel',
                'affiliate_url': 'https://www.duluthtrading.com/mens-work-clothing/?ref=YOUR_AFFILIATE_ID',
                'tagline': 'Fire Hose pants that survive a full demo day',
                'description': (
                    'Duluth Trading makes the toughest work pants and shirts in America. '
                    'Fire Hose pants are a cult favorite on skilled trade job sites. '
                    'Higher AOV than most apparel brands ($60–$120 per item). '
                    'Affiliate program via CJ Affiliate — 8% commission on all sales.'
                ),
                'commission_rate': '8%',
                'logo_url': '',
                'featured': False,
                'order': 11,
            },

            # ── EQUIPMENT ────────────────────────────────────────────────
            {
                'name': 'Sunbelt Rentals',
                'category': 'equipment',
                'affiliate_url': 'https://www.sunbeltrentals.com/?ref=YOUR_AFFILIATE_ID',
                'tagline': 'Equipment rental for Missouri GCs and subs',
                'description': (
                    'Sunbelt Rentals has multiple locations in the St. Louis metro and the ability '
                    'to deliver to job sites statewide. Contractors rent scissor lifts, forklifts, '
                    'generators, and compressors daily. Check Sunbelt\'s partner program for referral commissions. '
                    'Website: https://www.sunbeltrentals.com/about/affiliate/'
                ),
                'commission_rate': 'Contact Sunbelt for rates',
                'logo_url': '',
                'featured': False,
                'order': 12,
            },
        ]

        created = 0
        skipped = 0
        for aff_data in affiliates:
            from django.utils.text import slugify as _slugify
            slug = _slugify(aff_data['name'])
            if not dry_run:
                obj, created_flag = Affiliate.objects.get_or_create(
                    slug=slug,
                    defaults=aff_data,
                )
                if created_flag:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {aff_data["name"]} [{aff_data["category"]}]'))
                else:
                    skipped += 1
                    self.stdout.write(f'  ⚠  SKIP (exists): {aff_data["name"]}')
            else:
                self.stdout.write(f'  [DRY] {aff_data["name"]} — {aff_data["commission_rate"]}')

        self.stdout.write('\n' + '=' * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN — {len(affiliates)} affiliates would be created'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✅ Done! Created: {created}, Skipped: {skipped}\n'
                f'Next step: replace YOUR_ASSOCIATE_TAG / YOUR_AFFILIATE_ID placeholders '
                f'in the admin at /admin/construction/affiliate/'
            ))
