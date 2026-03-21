"""
Generate Daily Content - AI-Powered Article Creation

This management command automates article generation across all cities and sites.

Usage:
    python manage.py generate_daily_content
    python manage.py generate_daily_content --site seekingspringfield.com
    python manage.py generate_daily_content --city "Springfield, IL"
    python manage.py generate_daily_content --count 10
    python manage.py generate_daily_content --type tourism
    python manage.py generate_daily_content --dry-run

Course Module: youbetyourazure.com/courses/ai-content-automation
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from core.models import Site, City, Article
from core.ai_content_engine import DataAggregator, ContentPromptBuilder, AIContentEngine
import time


class Command(BaseCommand):
    help = 'Generate AI-powered articles for cities'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--site',
            type=str,
            help='Filter by site domain (e.g., seekingspringfield.com)'
        )
        
        parser.add_argument(
            '--city',
            type=str,
            help='Generate for specific city (format: "City Name, ST")'
        )
        
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of articles to generate per city (default: 1)'
        )
        
        parser.add_argument(
            '--type',
            type=str,
            default='city_guide',
            choices=['city_guide', 'demographics', 'tourism', 'living_here'],
            help='Type of article to generate'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating articles'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Generate even if similar article already exists'
        )
        
        parser.add_argument(
            '--api-key',
            type=str,
            help='OpenAI API key (defaults to environment variable)'
        )
    
    def handle(self, *args, **options):
        """Main execution"""
        
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("AI CONTENT GENERATION ENGINE"))
        self.stdout.write("=" * 80)
        self.stdout.write("")
        
        # Initialize AI engine
        api_key = options.get('api_key')
        engine = AIContentEngine(api_key=api_key)
        
        if not engine.api_key:
            self.stdout.write(self.style.ERROR("❌ No OpenAI API key found!"))
            self.stdout.write("")
            self.stdout.write("Set OPENAI_API_KEY in your .env file or use --api-key argument")
            return
        
        # Get cities to process
        cities = self._get_cities(options)
        
        if not cities.exists():
            self.stdout.write(self.style.WARNING("⚠️  No cities found matching criteria"))
            return
        
        # Get site for article assignment
        site = self._get_site(options)
        
        if not site:
            self.stdout.write(self.style.ERROR("❌ No site found!"))
            self.stdout.write("Specify --site or ensure cities have site associations")
            return
        
        # Stats tracking
        stats = {
            'generated': 0,
            'skipped': 0,
            'errors': 0,
            'total_words': 0,
            'total_tokens': 0,
        }
        
        article_type = options['type']
        count = options['count']
        dry_run = options['dry_run']
        force = options['force']
        
        total_cities = cities.count()
        
        self.stdout.write(f"📊 GENERATION PLAN:")
        self.stdout.write(f"   Cities: {total_cities}")
        self.stdout.write(f"   Articles per city: {count}")
        self.stdout.write(f"   Article type: {article_type}")
        self.stdout.write(f"   Site: {site.domain_name}")
        self.stdout.write(f"   Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        self.stdout.write("")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("🔍 DRY RUN MODE - No articles will be created"))
            self.stdout.write("")
        
        # Process each city
        for i, city in enumerate(cities, 1):
            self.stdout.write(f"[{i}/{total_cities}] Processing: {city.name}, {city.state}")
            
            # Check if article already exists
            if not force:
                existing = Article.objects.filter(
                    city=city,
                    site=site,
                    category=self._get_category_for_type(article_type),
                    ai_generated=True
                ).first()
                
                if existing:
                    self.stdout.write(self.style.WARNING(f"   ⏭️  Skipped - Article already exists (use --force to regenerate)"))
                    stats['skipped'] += 1
                    continue
            
            # Generate article(s)
            for article_num in range(count):
                try:
                    # Build prompt
                    aggregator = DataAggregator(city, census_data=city.census_data)
                    data = aggregator.aggregate()
                    
                    prompt_builder = ContentPromptBuilder(data)
                    prompt = prompt_builder.build_prompt(article_type)
                    
                    if dry_run:
                        self.stdout.write(f"   📝 Would generate: {article_type} article")
                        self.stdout.write(f"      Data sources: Census, {len(data.keys())} categories")
                        stats['generated'] += 1
                        continue
                    
                    # Generate content
                    self.stdout.write(f"   🤖 Generating {article_type} article...")
                    result = engine.generate_article(prompt)
                    
                    # Create article
                    article = Article.objects.create(
                        city=city,
                        site=site,
                        title=self._generate_title(city, article_type),
                        slug=self._generate_slug(city, article_type, article_num),
                        content=result['content'],
                        excerpt=self._generate_excerpt(result['content']),
                        category=self._get_category_for_type(article_type),
                        ai_generated=True,
                        ai_model_used=engine.model,
                        prompt_used=prompt[:500],  # Store first 500 chars for debugging
                        meta_description=self._generate_meta_description(city, result['content']),
                        keywords=self._generate_keywords(city, article_type),
                        published=False,  # Review before publishing
                        published_date=timezone.now(),  # Set current time
                    )
                    
                    # Update stats
                    stats['generated'] += 1
                    stats['total_words'] += result['word_count']
                    stats['total_tokens'] += result['tokens_used']
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"   ✅ Generated {result['word_count']} words "
                        f"({result['tokens_used']} tokens, "
                        f"Quality: {result['quality_score']:.0f}%)"
                    ))
                    
                    # Rate limiting - be nice to OpenAI
                    if article_num < count - 1:
                        time.sleep(1)
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"   ❌ Error: {str(e)}"))
                    stats['errors'] += 1
                    continue
            
            # Small delay between cities
            if i < total_cities:
                time.sleep(0.5)
        
        # Summary report
        self.stdout.write("")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS("📊 GENERATION SUMMARY"))
        self.stdout.write("=" * 80)
        self.stdout.write(f"Articles Generated: {stats['generated']}")
        self.stdout.write(f"Articles Skipped: {stats['skipped']}")
        self.stdout.write(f"Errors: {stats['errors']}")
        self.stdout.write(f"Total Words: {stats['total_words']:,}")
        self.stdout.write(f"Total Tokens: {stats['total_tokens']:,}")
        
        if stats['total_tokens'] > 0:
            # GPT-4 pricing: ~$0.03/1K tokens (input) + $0.06/1K tokens (output)
            # Rough estimate: $0.045/1K tokens average
            estimated_cost = (stats['total_tokens'] / 1000) * 0.045
            self.stdout.write(f"Estimated Cost: ${estimated_cost:.2f}")
        
        self.stdout.write("")
        
        if not dry_run and stats['generated'] > 0:
            self.stdout.write(self.style.WARNING("⚠️  IMPORTANT: Articles created as UNPUBLISHED"))
            self.stdout.write("Review in admin before publishing:")
            self.stdout.write(f"http://localhost:8002/admin/core/article/")
        
        self.stdout.write("=" * 80)
    
    def _get_cities(self, options):
        """Build queryset of cities to process"""
        
        queryset = City.objects.all()
        
        # Filter by site
        if options.get('site'):
            site_domain = options['site']
            queryset = queryset.filter(sites__domain_name=site_domain)
        
        # Filter by specific city
        if options.get('city'):
            city_str = options['city']
            if ',' in city_str:
                city_name, state = [s.strip() for s in city_str.split(',')]
                queryset = queryset.filter(name=city_name, state=state)
            else:
                queryset = queryset.filter(name=city_str)
        
        return queryset.distinct()
    
    def _get_site(self, options):
        """Get site for article assignment"""
        
        if options.get('site'):
            return Site.objects.filter(domain_name=options['site']).first()
        
        # Get first active site
        return Site.objects.filter(is_active=True).first()
    
    def _generate_title(self, city, article_type):
        """Generate SEO-friendly title"""
        
        if article_type == 'city_guide':
            return f"{city.name}, {city.state.name}: Complete City Guide 2026"
        elif article_type == 'demographics':
            return f"{city.name} Demographics & Population Data"
        elif article_type == 'tourism':
            return f"Visiting {city.name}: Top Attractions & Things to Do"
        elif article_type == 'living_here':
            return f"Living in {city.name}, {city.state.name}: What You Need to Know"
        else:
            return f"{city.name}, {city.state.name}"
    
    def _generate_slug(self, city, article_type, num=0):
        """Generate unique slug"""
        
        base = f"{city.name.lower()}-{city.state.abbreviation.lower()}-{article_type}"
        slug = slugify(base)
        
        if num > 0:
            slug = f"{slug}-{num}"
        
        # Ensure uniqueness
        counter = 1
        original_slug = slug
        while Article.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _generate_excerpt(self, content):
        """Extract first 2 sentences as excerpt"""
        
        sentences = content.split('.')[:2]
        excerpt = '. '.join(sentences) + '.'
        
        return excerpt[:300]  # Max 300 chars
    
    def _generate_meta_description(self, city, content):
        """Generate SEO meta description"""
        
        # Use first sentence
        first_sentence = content.split('.')[0] + '.'
        
        if len(first_sentence) > 160:
            return first_sentence[:157] + '...'
        
        return first_sentence
    
    def _generate_keywords(self, city, article_type):
        """Generate SEO keywords"""
        
        keywords = [
            city.name,
            city.state.abbreviation,
            f"{city.name} {city.state.abbreviation}",
        ]
        
        if article_type == 'city_guide':
            keywords.extend(['city guide', 'living in', 'moving to'])
        elif article_type == 'demographics':
            keywords.extend(['demographics', 'population', 'census data'])
        elif article_type == 'tourism':
            keywords.extend(['tourism', 'attractions', 'things to do', 'visit'])
        elif article_type == 'living_here':
            keywords.extend(['living in', 'quality of life', 'moving to'])
        
        return ', '.join(keywords)
    
    def _get_category_for_type(self, article_type):
        """Map article type to database category"""
        
        mapping = {
            'city_guide': 'GUIDE',
            'demographics': 'GOVERNMENT',
            'tourism': 'LIFESTYLE',
            'living_here': 'LIFESTYLE',
        }
        
        return mapping.get(article_type, 'NEWS')
