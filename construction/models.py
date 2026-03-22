from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone


class ProjectCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Project Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active / Under Construction'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        ProjectCategory, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='projects'
    )
    location = models.CharField(max_length=300, help_text='Street address or intersection')
    city = models.CharField(max_length=100, default='St. Louis')
    state = models.CharField(max_length=2, default='MO')
    description = models.TextField()
    contractor = models.CharField(max_length=200, blank=True)
    owner = models.CharField(max_length=200, blank=True, help_text='Project owner or client')
    architect = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    featured = models.BooleanField(default=False, help_text='Show on homepage')
    cover_image = models.ImageField(upload_to='projects/covers/', null=True, blank=True)
    facebook_post_url = models.URLField(blank=True, help_text='Facebook post URL — paste here after publishing to the Cardinals group')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-start_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('construction:project_detail', kwargs={'slug': self.slug})

    @property
    def image_count(self):
        return self.images.count()


def season_from_date(d):
    """Return the astronomical season for a given date.
    Spring:  Mar 20 – Jun 20
    Summer:  Jun 21 – Sep 22
    Fall:    Sep 23 – Dec 21
    Winter:  Dec 22 – Mar 19
    """
    if d is None:
        return ''
    m, day = d.month, d.day
    if (m == 3 and day >= 20) or (m in (4, 5)) or (m == 6 and day <= 20):
        return 'spring'
    if (m == 6 and day >= 21) or (m in (7, 8)) or (m == 9 and day <= 22):
        return 'summer'
    if (m == 9 and day >= 23) or (m in (10, 11)) or (m == 12 and day <= 21):
        return 'fall'
    return 'winter'


class GalleryImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/%Y/%m/')
    caption = models.CharField(max_length=400, blank=True)
    taken_date = models.DateField(null=True, blank=True, help_text='Date photo was taken')
    season = models.CharField(
        max_length=10,
        choices=[('spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall'), ('winter', 'Winter')],
        blank=True,
        help_text='Auto-calculated from date taken — or override manually'
    )
    order = models.PositiveIntegerField(default=0, help_text='Display order (lower = first)')
    featured = models.BooleanField(default=False, help_text='Use as project cover photo')
    ai_tags = models.JSONField(default=list, blank=True, help_text='Auto-generated tags from Azure AI Vision')
    ai_caption = models.TextField(blank=True, help_text='Auto-generated description from Azure AI Vision')

    class Meta:
        ordering = ['order', 'taken_date']

    def __str__(self):
        return f"{self.project.title} — {self.caption or self.pk}"

    def _run_ai_tagging(self):
        """Call Azure AI Vision to tag this image. Runs after image is in Azure Storage."""
        import os, requests as req
        endpoint = os.getenv('AZURE_VISION_ENDPOINT', '').rstrip('/')
        key = os.getenv('AZURE_VISION_KEY', '')
        if not endpoint or not key:
            return
        try:
            image_url = self.image.url
        except Exception:
            return
        # Computer Vision 3.2 Analyze API — tags + description caption
        url = f"{endpoint}/vision/v3.2/analyze?visualFeatures=Tags,Description"
        try:
            resp = req.post(
                url,
                json={'url': image_url},
                headers={'Ocp-Apim-Subscription-Key': key, 'Content-Type': 'application/json'},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            tags = [t['name'] for t in data.get('tags', []) if t.get('confidence', 0) >= 0.6]
            captions = data.get('description', {}).get('captions', [])
            caption_text = captions[0]['text'] if captions else ''
            GalleryImage.objects.filter(pk=self.pk).update(ai_tags=tags, ai_caption=caption_text)
        except Exception:
            pass  # Never block a save due to Vision API failure

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        # Auto-calculate season from taken_date if not manually set
        if self.taken_date and not self.season:
            self.season = season_from_date(self.taken_date)
        super().save(*args, **kwargs)
        # Run AI tagging on new images (after save so image is in Azure Storage)
        if is_new and self.image and not self.ai_tags:
            self._run_ai_tagging()


class BidOpportunity(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open — Accepting Bids'),
        ('closed', 'Closed'),
        ('awarded', 'Awarded'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=300)
    agency = models.CharField(max_length=200, help_text='Issuing agency or organization')
    bid_number = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, default='MO')
    due_date = models.DateField(null=True, blank=True)
    posted_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    estimated_value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        help_text='Estimated project value in dollars'
    )
    external_url = models.URLField(blank=True, help_text='Link to official bid document')
    contact_name = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['due_date', '-posted_date']
        verbose_name_plural = 'Bid Opportunities'

    def __str__(self):
        return f"{self.title} — {self.agency}"


class PermitRecord(models.Model):
    permit_number = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100, default='Springfield')
    state = models.CharField(max_length=2, default='MO')
    permit_type = models.CharField(max_length=100, help_text='e.g., Commercial Build, Residential, Demolition')
    description = models.TextField(blank=True)
    contractor = models.CharField(max_length=200, blank=True)
    owner = models.CharField(max_length=200, blank=True)
    issued_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True, help_text='e.g., Active, Finaled, Expired')
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    source_url = models.URLField(blank=True, help_text='Source of public record')

    class Meta:
        ordering = ['-issued_date']
        verbose_name_plural = 'Permit Records'

    def __str__(self):
        return f"Permit {self.permit_number} — {self.address}"


class Affiliate(models.Model):
    """
    Affiliate partner programs displayed on Missouri Construction pages.
    Categories: hand tools, power tools, software (AutoCAD), safety gear, apparel.
    Earn commissions by referring contractors and builders to these products.
    """
    CATEGORY_CHOICES = [
        ('hand_tools', 'Hand Tools'),
        ('power_tools', 'Power Tools'),
        ('software', 'Software & CAD'),
        ('safety', 'Safety & PPE'),
        ('apparel', 'Work Apparel'),
        ('equipment', 'Heavy Equipment'),
        ('materials', 'Building Materials'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    affiliate_url = models.URLField(help_text='Tracking URL with your affiliate ID')
    tagline = models.CharField(max_length=200, blank=True, help_text='Short value proposition')
    description = models.TextField(blank=True)
    commission_rate = models.CharField(max_length=50, blank=True, help_text='e.g., "8%" or "4-6%"')
    logo_url = models.URLField(blank=True, help_text='External logo image URL')
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False, help_text='Show in homepage sidebar')
    order = models.PositiveIntegerField(default=0, help_text='Sort order (lower = first)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'order', 'name']
        verbose_name_plural = 'Affiliates'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# ST. LOUIS BUILDING CONVERSION ANALYSIS
# ---------------------------------------------------------------------------

class Neighborhood(models.Model):
    DISTRICT_CHOICES = [
        ('downtown', 'Downtown'),
        ('midtown', 'Midtown / Grand Center'),
        ('northside', 'North Side'),
        ('southside', 'South Side'),
        ('central_west_end', 'Central West End'),
        ('slu_corridor', 'SLU / Grand Center Corridor'),
        ('bjc_corridor', 'BJC / Forest Park Medical Corridor'),
        ('lafayette_sq', 'Lafayette Square'),
        ('soulard', 'Soulard'),
        ('benton_park', 'Benton Park'),
        ('tower_grove', 'Tower Grove'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    district = models.CharField(max_length=20, choices=DISTRICT_CHOICES, default='downtown')
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    crime_index = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True,
                                      help_text='Relative crime index (100 = national average)')
    walk_score = models.IntegerField(null=True, blank=True, help_text='Walk Score 0–100')
    transit_score = models.IntegerField(null=True, blank=True, help_text='Transit Score 0–100')
    nearby_universities = models.JSONField(default=list, blank=True,
                                           help_text='e.g. ["SLU", "UMSL", "WashU"]')
    nearby_hospitals = models.JSONField(default=list, blank=True,
                                        help_text='e.g. ["Barnes-Jewish", "SSM Health"]')
    grocery_stores = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['district', 'name']
        verbose_name_plural = 'Neighborhoods'

    def __str__(self):
        return f"{self.name} ({self.get_district_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TIFDistrict(models.Model):
    name = models.CharField(max_length=200)
    district_number = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True,
                                       help_text='Total TIF amount authorized')
    term_years = models.IntegerField(null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    sldc_url = models.URLField(blank=True, help_text='SLDC public records URL')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'TIF District'
        verbose_name_plural = 'TIF Districts'

    def __str__(self):
        return self.name


class BuildingConversion(models.Model):
    BUILDING_TYPE_CHOICES = [
        ('hotel', 'Hotel'),
        ('office', 'Office Building'),
        ('warehouse', 'Warehouse / Industrial'),
        ('retail', 'Retail / Department Store'),
        ('mixed', 'Mixed Use'),
        ('bank', 'Bank / Financial'),
        ('school', 'School / University'),
        ('other', 'Other'),
    ]
    CONVERSION_TYPE_CHOICES = [
        ('residential', 'Residential (Apartments / Condos)'),
        ('mixed_residential', 'Mixed Use with Residential'),
        ('commercial', 'Commercial Redevelopment'),
        ('hospitality', 'Hospitality'),
    ]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned / Approved'),
        ('stalled', 'Stalled'),
    ]
    UNIT_TYPE_CHOICES = [
        ('condo', 'Condominiums'),
        ('apartment', 'Apartments'),
        ('mixed', 'Mixed Condo / Apartment'),
    ]

    name = models.CharField(max_length=200, help_text='Display name, e.g. "Majestic Hotel → Majestic Condos"')
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    original_name = models.CharField(max_length=200, blank=True)
    current_name = models.CharField(max_length=200, blank=True)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='conversions')
    tif_district = models.ForeignKey(TIFDistrict, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='conversions')
    address = models.CharField(max_length=300)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    original_building_type = models.CharField(max_length=20, choices=BUILDING_TYPE_CHOICES)
    conversion_type = models.CharField(max_length=20, choices=CONVERSION_TYPE_CHOICES, default='residential')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    # Before
    original_units = models.IntegerField(null=True, blank=True,
                                         help_text='Hotel rooms, building floors, or sq ft')
    original_unit_label = models.CharField(max_length=50, default='rooms',
                                           help_text='rooms / sq ft / floors / suites')
    year_built = models.IntegerField(null=True, blank=True)
    # After
    residential_units = models.IntegerField(null=True, blank=True)
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES, default='apartment')
    completion_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    developer = models.CharField(max_length=200, blank=True)
    architect = models.CharField(max_length=200, blank=True)
    general_contractor = models.CharField(max_length=200, blank=True)
    cover_image_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True, help_text='SLDC, news article, or permit source URL')
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-completion_year', 'neighborhood', 'name']
        verbose_name = 'Building Conversion'
        verbose_name_plural = 'Building Conversions'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def unit_delta(self):
        if self.residential_units and self.original_units:
            return self.residential_units - self.original_units
        return None


class ConversionFinancials(models.Model):
    CONFIDENCE_CHOICES = [
        ('high', 'High — Public Records'),
        ('medium', 'Medium — News / Press Release'),
        ('estimate', 'Estimated / Derived'),
    ]

    building = models.OneToOneField(BuildingConversion, on_delete=models.CASCADE,
                                    related_name='financials')
    # Acquisition
    purchase_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    purchase_year = models.IntegerField(null=True, blank=True)
    assessed_value_before = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    assessed_value_after = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Rehab
    rehab_cost_estimate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    total_project_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Incentives
    tif_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True,
                                     help_text='TIF subsidy amount')
    historic_tax_credits = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    nmtc_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True,
                                      help_text='New Markets Tax Credits')
    other_incentives = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    # Unit economics
    avg_sale_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True,
                                         help_text='Average condo sale price')
    avg_rent_monthly = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                           help_text='Average monthly rent')
    avg_hoa_monthly = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    avg_property_tax_annual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Data quality
    data_confidence = models.CharField(max_length=10, choices=CONFIDENCE_CHOICES, default='medium')
    data_sources = models.TextField(blank=True, help_text='Sources: SLDC, STLToday, permit records…')
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conversion Financials'
        verbose_name_plural = 'Conversion Financials'

    def __str__(self):
        return f"Financials — {self.building.name}"

    @property
    def total_public_subsidy(self):
        total = 0
        for field in [self.tif_amount, self.historic_tax_credits,
                      self.nmtc_amount, self.other_incentives]:
            if field:
                total += field
        return total or None

    @property
    def cost_per_unit(self):
        if self.total_project_cost and self.building.residential_units:
            return self.total_project_cost / self.building.residential_units
        return None


# ---------------------------------------------------------------------------
# Subscription System
# ---------------------------------------------------------------------------

class SubscriptionPlan(models.Model):
    TIER_CHOICES = [
        ('scout', 'Scout'),
        ('analyst', 'Analyst'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    INTERVAL_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]

    tier = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    tagline = models.CharField(max_length=200, blank=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    price_annual = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                       help_text='Annual price (shown as /yr)')
    stripe_price_id_monthly = models.CharField(max_length=100, blank=True,
                                               help_text='Stripe Price ID for monthly billing')
    stripe_price_id_annual = models.CharField(max_length=100, blank=True,
                                              help_text='Stripe Price ID for annual billing')
    # Feature flags
    show_financials = models.BooleanField(default=False,
                                          help_text='Access to TIF, tax credit, rehab cost data')
    show_comparables = models.BooleanField(default=False,
                                           help_text='Access to comparable sale/rent analysis')
    show_powerbi = models.BooleanField(default=False,
                                       help_text='Embedded Power BI dashboards')
    api_access = models.BooleanField(default=False,
                                     help_text='REST API access for bulk data export')
    custom_reports = models.BooleanField(default=False,
                                         help_text='Custom on-demand analysis reports')
    max_reports_monthly = models.IntegerField(default=0,
                                              help_text='0 = unlimited; custom report quota')
    # Display
    highlight = models.BooleanField(default=False, help_text='Mark as "Most Popular" on pricing page')
    features_list = models.JSONField(default=list, blank=True,
                                     help_text='Ordered list of bullet points shown on pricing card')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Subscription Plan'
        verbose_name_plural = 'Subscription Plans'

    def __str__(self):
        return f"{self.name} — ${self.price_monthly}/mo"

    @property
    def is_free(self):
        return self.price_monthly == 0


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('trialing', 'Trialing'),
        ('past_due', 'Past Due'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    INTERVAL_CHOICES = [
        ('monthly', 'Monthly'),
        ('annual', 'Annual'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT,
                              related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES, default='monthly')
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Subscription'
        verbose_name_plural = 'User Subscriptions'

    def __str__(self):
        return f"{self.user.email} — {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        if self.status in ('active', 'trialing'):
            return True
        if self.status == 'past_due':
            # Grace period: allow access for 3 days after period end
            if self.current_period_end:
                grace = self.current_period_end + timezone.timedelta(days=3)
                return timezone.now() < grace
        return False

    @property
    def is_paid(self):
        return self.is_active and not self.plan.is_free


# ---------------------------------------------------------------------------
# Power BI Report Registry
# ---------------------------------------------------------------------------

class PowerBIReport(models.Model):
    """
    Stores Power BI report metadata for embedding.
    Supports both public (publish-to-web) and private (embed token) modes.
    """
    SCOPE_CHOICES = [
        ('building', 'Building Conversion'),
        ('neighborhood', 'Neighborhood'),
        ('citywide', 'Citywide / Statewide'),
        ('custom', 'Custom / Client-Specific'),
    ]
    EMBED_MODE_CHOICES = [
        ('public', 'Public — Publish to Web iframe'),
        ('private', 'Private — Azure AD Embed Token (subscriber-gated)'),
    ]

    name = models.CharField(max_length=200, help_text='e.g. "Downtown Hotel Conversions Financial Overview"')
    slug = models.SlugField(unique=True, max_length=200)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='citywide')
    embed_mode = models.CharField(max_length=10, choices=EMBED_MODE_CHOICES, default='private')

    # If attached to a specific building or neighborhood
    building = models.ForeignKey(
        'BuildingConversion', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='pbi_reports',
    )
    neighborhood = models.ForeignKey(
        'Neighborhood', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='pbi_reports',
    )

    # Power BI identifiers (from powerbi.com → your workspace)
    workspace_id = models.CharField(
        max_length=100, blank=True,
        help_text='Power BI Workspace (Group) ID — from URL: app.powerbi.com/groups/{workspace_id}',
    )
    report_id = models.CharField(
        max_length=100, blank=True,
        help_text='Power BI Report ID — from URL: .../reports/{report_id}',
    )
    dataset_id = models.CharField(
        max_length=100, blank=True,
        help_text='Power BI Dataset ID (needed for embed token generation)',
    )

    # Public embed: copy the full src URL from "Publish to web" dialog
    public_embed_url = models.URLField(
        max_length=500, blank=True,
        help_text='Full iframe src from Power BI "Publish to web" — used when embed_mode=public',
    )

    # Display
    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    default_height_px = models.IntegerField(default=600)

    # Access control (minimum subscription tier to view)
    min_tier = models.CharField(
        max_length=20,
        choices=[
            ('scout', 'Scout (free)'),
            ('analyst', 'Analyst ($29/mo)'),
            ('professional', 'Professional ($149/mo)'),
            ('enterprise', 'Enterprise ($499/mo)'),
        ],
        default='professional',
    )

    featured = models.BooleanField(default=False, help_text='Show on the STL Conversions overview page')
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    TIER_ORDER = ['scout', 'analyst', 'professional', 'enterprise']

    class Meta:
        ordering = ['scope', 'name']
        verbose_name = 'Power BI Report'
        verbose_name_plural = 'Power BI Reports'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def user_can_view(self, user):
        """Return True if this user's subscription tier meets the minimum."""
        if not user.is_authenticated:
            return self.min_tier == 'scout'
        if user.is_staff:
            return True
        sub = getattr(user, 'subscription', None)
        if not sub or not sub.is_active:
            return self.min_tier == 'scout'
        try:
            user_idx = self.TIER_ORDER.index(sub.plan.tier)
            min_idx = self.TIER_ORDER.index(self.min_tier)
            return user_idx >= min_idx
        except ValueError:
            return False
