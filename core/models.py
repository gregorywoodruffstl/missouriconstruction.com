""" I don't know what the **** is going on
Core models for the Missouri Construction multi-site ecosystem.
These models are shared across ALL sites (SeekingSpringfield, Landscaping St Louis, etc.)
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Site(models.Model):
    """
    Represents each domain in the portfolio (seekingspringfield.com, etc.)
    Links to Domain model in CloudandSecureLimitedII.com portal
    """
    SITE_TYPE_CHOICES = [
        ('SEEKING', 'Seeking City Directory'),
        ('INDUSTRY', 'Industry-Specific Directory'),
        ('MARKETING', 'Marketing Site'),
        ('EDUCATIONAL', 'Educational Hub'),
    ]
    
    domain_name = models.CharField(max_length=255, unique=True)
    site_type = models.CharField(max_length=20, choices=SITE_TYPE_CHOICES)
    display_name = models.CharField(max_length=255)  # "Seeking Springfield"
    primary_color = models.CharField(max_length=7, default='#0078D4')  # Hex color
    google_analytics_id = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    launch_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.domain_name


class State(models.Model):
    """
    US State information - state flower, tree, symbols
    Displayed in SeekingSpringfield.com header for local pride!
    """
    name = models.CharField(max_length=100, unique=True)  # "Missouri"
    abbreviation = models.CharField(max_length=2, unique=True)  # "MO"
    capital = models.CharField(max_length=100, blank=True)  # "Jefferson City"
    
    # State Symbols (USER REQUESTED for header!)
    state_flower = models.CharField(max_length=100, blank=True)  # "White Hawthorn Blossom"
    state_tree = models.CharField(max_length=100, blank=True)  # "Flowering Dogwood"
    state_bird = models.CharField(max_length=100, blank=True)  # "Eastern Bluebird"
    state_motto = models.CharField(max_length=255, blank=True)  # "Salus populi suprema lex esto"
    
    # Geography
    region = models.CharField(max_length=50, blank=True)  # "Midwest", "Northeast", etc.
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class City(models.Model):
    """
    Represents a city (e.g., Springfield, Illinois)
    One city can appear on multiple sites
    """
    name = models.CharField(max_length=255)  # "Springfield"
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')  # Link to State model
    state_abbr = models.CharField(max_length=2, blank=True)  # "IL" - redundant but useful for queries
    country = models.CharField(max_length=100, default='USA')
    
    # Census Data
    population = models.IntegerField(null=True, blank=True)
    median_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    census_data = models.JSONField(default=dict, blank=True)  # Full census JSON
    last_census_updated = models.DateTimeField(null=True, blank=True)
    
    # Geo Data (USER REQUESTED for header display!)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Site Association
    sites = models.ManyToManyField(Site, related_name='cities')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Cities'
        unique_together = ['name', 'state', 'country']
        ordering = ['state', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.state.abbreviation if self.state else self.state_abbr}"
    
    @property
    def full_name(self):
        return f"{self.name}, {self.state.name if self.state else 'Unknown'}, {self.country}"
    
    @property
    def coordinates_display(self):
        """Format coordinates for header display: '37.2090° N, 93.2923° W'"""
        if not self.latitude or not self.longitude:
            return ""
        
        lat_dir = "N" if self.latitude >= 0 else "S"
        lon_dir = "E" if self.longitude >= 0 else "W"
        
        return f"{abs(self.latitude):.4f}° {lat_dir}, {abs(self.longitude):.4f}° {lon_dir}"


class Article(models.Model):
    """
    AI-generated content for cities
    Think of this as your "inventory" - like products on shelves
    """
    CATEGORY_CHOICES = [
        ('NEWS', 'Local News'),
        ('EVENTS', 'Events & Activities'),
        ('BUSINESS', 'Business & Economy'),
        ('GOVERNMENT', 'Government & Politics'),
        ('EDUCATION', 'Education'),
        ('LIFESTYLE', 'Lifestyle & Culture'),
        ('REAL_ESTATE', 'Real Estate & Construction'),
        ('GUIDE', 'City Guide'),
        ('SPORTS', 'Sports'),
    ]
    
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='articles')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='articles')
    
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=600, unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # AI Tracking
    ai_generated = models.BooleanField(default=True)
    ai_model_used = models.CharField(max_length=50, default='gpt-4')
    source_url = models.URLField(blank=True)  # Original news source for attribution
    prompt_used = models.TextField(blank=True)  # For debugging/improving AI
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    
    # Performance Tracking (Your "Point of Sale" data)
    view_count = models.IntegerField(default=0)
    share_count = models.IntegerField(default=0)
    last_viewed = models.DateTimeField(null=True, blank=True)
    
    # Publishing
    published = models.BooleanField(default=True)
    published_date = models.DateTimeField(default=timezone.now)
    featured = models.BooleanField(default=False)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['city', '-published_date']),
            models.Index(fields=['site', '-published_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.city})"
    
    def record_view(self):
        """Increment view count - your POS data"""
        self.view_count += 1
        self.last_viewed = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed'])


class Business(models.Model):
    """
    Business directory listings
    Free tier + Premium tier ($50/month) + Featured tier ($150/month)
    """
    CATEGORY_CHOICES = [
        ('CONSTRUCTION', 'Construction & Contractors'),
        ('LANDSCAPING', 'Landscaping & Lawn Care'),
        ('REAL_ESTATE', 'Real Estate'),
        ('RESTAURANT', 'Restaurant & Dining'),
        ('RETAIL', 'Retail & Shopping'),
        ('SERVICES', 'Professional Services'),
        ('HEALTHCARE', 'Healthcare'),
        ('EDUCATION', 'Education'),
        ('ENTERTAINMENT', 'Entertainment & Arts'),
        ('OTHER', 'Other'),
    ]
    
    TIER_CHOICES = [
        ('FREE', 'Free Listing'),
        ('PREMIUM', 'Premium ($50/month)'),
        ('FEATURED', 'Featured ($150/month)'),
    ]
    
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='businesses')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='businesses')
    
    # Basic Info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    
    # Contact
    address = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Tier & Revenue (USER REQUESTED: 30-day free trial)
    tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='FREE')
    monthly_cost = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    free_trial_ends = models.DateField(null=True, blank=True)  # 30-day free trial
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    
    # Premium Features
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)
    photos = models.JSONField(default=list, blank=True)  # Array of image URLs
    featured_until = models.DateField(null=True, blank=True)
    
    # Business Owners (ManyToMany - multiple people can manage one business)
    managers = models.ManyToManyField(User, related_name='managed_businesses', blank=True)
    
    # Tracking
    view_count = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)  # Phone/website clicks
    
    # Meta
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-tier', '-featured_until', 'name']
        unique_together = ['site', 'slug']
    
    def __str__(self):
        return f"{self.name} ({self.city}) - {self.tier}"
    
    @property
    def is_premium(self):
        return self.tier in ['PREMIUM', 'FEATURED']
    
    @property
    def on_free_trial(self):
        """Check if business is currently on 30-day free trial"""
        if not self.free_trial_ends:
            return False
        from django.utils import timezone
        return timezone.now().date() <= self.free_trial_ends
    
    @property
    def average_rating(self):
        """Calculate average rating from approved reviews"""
        approved_reviews = self.reviews.filter(approved=True)
        if not approved_reviews.exists():
            return 0
        total = sum(review.rating for review in approved_reviews)
        return round(total / approved_reviews.count(), 1)
    
    @property
    def review_count_display(self):
        """Get count of approved reviews only"""
        return self.reviews.filter(approved=True).count()


class Event(models.Model):
    """
    Local events (AI-scraped from city calendars, Eventbrite, etc.)
    """
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='events')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='events')
    
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=600)
    description = models.TextField(blank=True)
    
    # Event Details
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=500, blank=True)
    organizer = models.CharField(max_length=255, blank=True)
    
    # Links
    event_url = models.URLField(blank=True)
    ticket_url = models.URLField(blank=True)
    
    # AI Tracking
    ai_scraped = models.BooleanField(default=True)
    source_url = models.URLField(blank=True)
    source = models.ForeignKey(
        'EventSource', on_delete=models.SET_NULL, null=True, blank=True, related_name='events'
    )
    # SHA-1 fingerprint (city + title + start_date) for deduplication
    fingerprint = models.CharField(max_length=64, blank=True, db_index=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.city} ({self.start_date.date()})"


class EventSource(models.Model):
    """
    Registry of municipal/civic calendar sources for each Springfield city.
    Stores URL, feed type, and last-fetch metadata so the management command
    knows where to pull events from for each city.

    Feed types supported:
      ICAL  — standard iCalendar (.ics) feed
      RSS   — RSS/Atom feed with event entries
      SOCRATA — Socrata Open Data API (json)
      HTML  — HTML scrape (last resort, fragile)
    """
    FEED_TYPE_CHOICES = [
        ('ICAL', 'iCalendar (.ics)'),
        ('RSS', 'RSS / Atom Feed'),
        ('SOCRATA', 'Socrata Open Data API'),
        ('HTML', 'HTML Scrape'),
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='event_sources')
    name = models.CharField(max_length=255)          # "Springfield IL City Hall Calendar"
    feed_url = models.URLField()                     # The actual URL to fetch
    feed_type = models.CharField(max_length=10, choices=FEED_TYPE_CHOICES, default='ICAL')
    is_active = models.BooleanField(default=True)

    # Track fetch health
    last_fetched = models.DateTimeField(null=True, blank=True)
    last_success = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    consecutive_failures = models.IntegerField(default=0)

    # City hall / municipal office contact info (bonus context for the platform)
    municipal_office_name = models.CharField(max_length=255, blank=True)
    municipal_office_url = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['city__state__abbreviation', 'city__name']
        verbose_name = 'Event Source'
        verbose_name_plural = 'Event Sources'

    def __str__(self):
        return f"{self.name} ({self.city}) [{self.feed_type}]"

    def mark_success(self):
        from django.utils import timezone as tz
        self.last_fetched = tz.now()
        self.last_success = tz.now()
        self.consecutive_failures = 0
        self.last_error = ''
        self.save(update_fields=['last_fetched', 'last_success', 'consecutive_failures', 'last_error'])

    def mark_failure(self, error: str):
        from django.utils import timezone as tz
        self.last_fetched = tz.now()
        self.consecutive_failures += 1
        self.last_error = error[:1000]
        # Auto-disable after 10 straight failures
        if self.consecutive_failures >= 10:
            self.is_active = False
        self.save(update_fields=['last_fetched', 'consecutive_failures', 'last_error', 'is_active'])



    """
    Daily analytics snapshot - Your "Point of Sale" dashboard
    Tracks which articles/cities are performing (like inventory turns)
    """
    date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)
    
    # Daily Metrics
    page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    avg_time_on_page = models.IntegerField(default=0)  # seconds
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Revenue (AdSense estimate)
    estimated_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ['date', 'site', 'article']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.site} - {self.date} ({self.page_views} views)"


# ============================================================================
# USER REGISTRATION MODELS (USER REQUESTED - Citizens first!)
# ============================================================================

from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Extended user profile for Citizens (FREE) and Business Owners (PAID)
    USER STRATEGY: Citizens register free → See value → Tell boss → Boss pays Premium
    """
    USER_TYPE_CHOICES = [
        ('CITIZEN', 'Citizen/Resident'),
        ('BUSINESS', 'Business Owner'),
        ('ADMIN', 'Site Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='CITIZEN')
    
    # Default City Preference (Cookie/IP-based with user override)
    default_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='default_users')
    
    # Contact
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    
    # Email Preferences (Weekly digest, new businesses, events)
    email_weekly_digest = models.BooleanField(default=True)
    email_new_businesses = models.BooleanField(default=True)
    email_new_events = models.BooleanField(default=True)
    
    # Engagement Tracking (Leaderboards, badges, gamification)
    review_count = models.IntegerField(default=0)
    event_submissions = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    bookmark_count = models.IntegerField(default=0)
    
    # Verification (USER REQUESTED: Email link)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe (for business owners with Premium/Featured subscriptions)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    @property
    def is_business_owner(self):
        return self.user_type == 'BUSINESS'


# Auto-create UserProfile when User registers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class BusinessReview(models.Model):
    """
    Citizen reviews of businesses (like Google/Yelp)
    USER REQUESTED: Admin approval initially, auto-approve later when trust builds
    """
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')
    
    # Review Content
    rating = models.IntegerField(choices=[(1,'⭐'), (2,'⭐⭐'), (3,'⭐⭐⭐'), (4,'⭐⭐⭐⭐'), (5,'⭐⭐⭐⭐⭐')])
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Photos (optional - citizens can upload)
    photos = models.JSONField(default=list, blank=True)
    
    # Moderation (USER REQUESTED: Admin approval initially)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews_approved')
    
    flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=500, blank=True)
    
    # Business Response (business owner can reply)
    business_response = models.TextField(blank=True)
    business_response_date = models.DateTimeField(null=True, blank=True)
    
    # Helpfulness voting (other citizens vote helpful/not)
    helpful_count = models.IntegerField(default=0)
    not_helpful_count = models.IntegerField(default=0)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['business', 'user']  # One review per user per business
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', '-created_at']),
            models.Index(fields=['approved', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} reviewed {self.business.name} - {self.rating}⭐"
    
    @property
    def helpfulness_score(self):
        """Calculate helpfulness percentage"""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return int((self.helpful_count / total) * 100)


class BusinessClaim(models.Model):
    """
    Business ownership verification process
    USER REQUESTED: Email link verification (simple and effective)
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified - Approved'),
        ('REJECTED', 'Rejected - Denied'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='claims')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_claims')
    
    # Verification (USER REQUESTED: Email link)
    verification_method = models.CharField(max_length=20, default='EMAIL')
    verification_token = models.CharField(max_length=100)
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Admin Review (if needed for suspicious claims)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claims_reviewed')
    review_notes = models.TextField(blank=True)
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} claims {self.business.name} ({self.status})"


class CityImage(models.Model):
    """
    User-uploaded photos for each Springfield city.
    Images go to Azure Blob Storage. AI vision tags are generated automatically on upload.
    """
    city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='images')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='city_images')
    image = models.ImageField(upload_to='city_images/%Y/%m/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    # AI Vision fields — populated automatically by GPT-4o on upload
    ai_description = models.TextField(blank=True)
    ai_tags = models.JSONField(default=list)
    ai_flagged = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['city', '-uploaded_at']),
            models.Index(fields=['is_approved', '-uploaded_at']),
        ]

    def __str__(self):
        return f"{self.uploaded_by.username} — {self.city.name} ({self.uploaded_at:%Y-%m-%d})"


# ============================================================================
# MARKETPLACE MODELS
# Businesses list products → Customers buy → Platform takes a fee → Business fulfills
# ============================================================================

class Product(models.Model):
    """
    Items posted for sale by a registered business.
    Business handles all fulfillment; platform collects a percentage fee.
    """
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('USED', 'Used – Like New'),
        ('GOOD', 'Used – Good'),
        ('FAIR', 'Used – Fair'),
        ('DIGITAL', 'Digital / Service'),
    ]

    CATEGORY_CHOICES = [
        ('HOME', 'Home & Garden'),
        ('CLOTHING', 'Clothing & Accessories'),
        ('FOOD', 'Food & Beverage'),
        ('ELECTRONICS', 'Electronics'),
        ('SPORTS', 'Sports & Outdoors'),
        ('SERVICES', 'Services'),
        ('AUTOMOTIVE', 'Automotive'),
        ('KIDS', 'Kids & Baby'),
        ('COLLECTIBLES', 'Collectibles & Antiques'),
        ('OTHER', 'Other'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='products')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='products')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='products')

    # Core fields
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='NEW')

    # Images — first entry is the primary/hero image
    images = models.JSONField(default=list, blank=True)  # list of Azure Blob URLs
    primary_image = models.ImageField(upload_to='product_images/%Y/%m/', null=True, blank=True)

    # Inventory
    quantity_available = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # Admin must approve before going live

    # AI moderation (same pattern as CityImage)
    ai_flagged = models.BooleanField(default=False)
    ai_flag_reason = models.CharField(max_length=500, blank=True)

    # Stats
    view_count = models.IntegerField(default=0)
    sold_count = models.IntegerField(default=0)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business', 'is_active', 'is_approved']),
            models.Index(fields=['city', 'is_active', 'is_approved']),
        ]

    def __str__(self):
        return f"{self.name} — {self.business.name}"

    @property
    def current_price(self):
        """Return sale price if set, otherwise regular price."""
        if self.sale_price and self.sale_price < self.price:
            return self.sale_price
        return self.price

    @property
    def on_sale(self):
        return bool(self.sale_price and self.sale_price < self.price)

    @property
    def hero_image_url(self):
        if self.primary_image:
            return self.primary_image.url
        if self.images:
            return self.images[0]
        return None


class Order(models.Model):
    """
    A completed (or pending) purchase through the Seeking Springfield marketplace.
    Platform fee is collected at checkout; business fulfills the order.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid — Awaiting Fulfillment'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]

    # Buyer — allow guest checkout (buyer is null for guests)
    buyer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders'
    )
    guest_email = models.EmailField(blank=True)

    # Stripe
    stripe_checkout_session_id = models.CharField(max_length=200, blank=True, unique=True, null=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    # Financials (stored in dollars, not cents)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Shipping
    shipping_name = models.CharField(max_length=255, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)  # Stripe-provided address

    # Reference
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='orders')

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        buyer_label = self.buyer.username if self.buyer else self.guest_email
        return f"Order #{self.pk} — {buyer_label} — {self.status}"

    def calculate_totals(self, fee_percent=10):
        """Recalculate subtotal and platform fee from order items."""
        from decimal import Decimal
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.platform_fee = (self.subtotal * Decimal(fee_percent) / 100).quantize(Decimal('0.01'))
        self.total = self.subtotal
        self.save(update_fields=['subtotal', 'platform_fee', 'total'])


class OrderItem(models.Model):
    """
    Individual line item within an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name='order_items')

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot at purchase time

    class Meta:
        ordering = ['id']

    @property
    def subtotal(self):
        from decimal import Decimal
        return (self.unit_price * self.quantity).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order.pk})"


class Bookmark(models.Model):
    """
    Citizen bookmarks for businesses, articles, events
    """
    BOOKMARK_TYPE_CHOICES = [
        ('BUSINESS', 'Business'),
        ('ARTICLE', 'Article'),
        ('EVENT', 'Event'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    bookmark_type = models.CharField(max_length=10, choices=BOOKMARK_TYPE_CHOICES)
    
    # Polymorphic relations (only one will be set)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='bookmarked_by')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ['user', 'business'],
            ['user', 'article'],
            ['user', 'event'],
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.business:
            return f"{self.user.username} bookmarked {self.business.name}"
        elif self.article:
            return f"{self.user.username} bookmarked {self.article.title}"
        elif self.event:
            return f"{self.user.username} bookmarked {self.event.title}"
        return f"{self.user.username} bookmark"
