from django.contrib import admin
from .models import (ProjectCategory, Project, GalleryImage, BidOpportunity,
                     PermitRecord, Affiliate, Neighborhood, TIFDistrict,
                     BuildingConversion, ConversionFinancials,
                     SubscriptionPlan, UserSubscription, PowerBIReport)


class GalleryImageInline(admin.StackedInline):
    model = GalleryImage
    extra = 1
    fields = ('image', 'caption', 'taken_date', 'season', 'order', 'featured')
    verbose_name = 'Photo'
    verbose_name_plural = 'Photos — click "Add another Photo" below to add more. Use "Save and continue editing" (not "Save and add another") to stay on this project.'
    show_change_link = True


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'state', 'status', 'contractor', 'start_date', 'end_date', 'featured', 'image_count')
    list_filter = ('status', 'state', 'city', 'featured', 'category')
    search_fields = ('title', 'location', 'contractor', 'owner', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryImageInline]
    fieldsets = (
        ('Project Info', {
            'fields': ('title', 'slug', 'category', 'description', 'cover_image', 'featured')
        }),
        ('Location', {
            'fields': ('location', 'city', 'state')
        }),
        ('Parties', {
            'fields': ('contractor', 'owner', 'architect')
        }),
        ('Timeline & Cost', {
            'fields': ('status', 'start_date', 'end_date', 'estimated_cost')
        }),
    )

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Photos'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'caption', 'taken_date', 'season', 'order', 'featured')
    list_filter = ('project', 'season', 'featured')
    search_fields = ('caption', 'project__title')


@admin.register(BidOpportunity)
class BidOpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'agency', 'city', 'state', 'due_date', 'status', 'estimated_value')
    list_filter = ('status', 'state', 'city')
    search_fields = ('title', 'agency', 'bid_number', 'description')


@admin.register(PermitRecord)
class PermitRecordAdmin(admin.ModelAdmin):
    list_display = ('permit_number', 'address', 'city', 'state', 'permit_type', 'issued_date', 'status', 'estimated_value')
    list_filter = ('city', 'state', 'permit_type', 'status')
    search_fields = ('permit_number', 'address', 'contractor', 'description')


@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'commission_rate', 'featured', 'active', 'order')
    list_filter = ('category', 'active', 'featured')
    search_fields = ('name', 'description', 'tagline')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('featured', 'active', 'order')


# ---------------------------------------------------------------------------
# ST. LOUIS BUILDING CONVERSION ANALYSIS
# ---------------------------------------------------------------------------

@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'walk_score', 'transit_score', 'crime_index')
    list_filter = ('district',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TIFDistrict)
class TIFDistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'district_number', 'total_amount', 'term_years',
                    'established_date', 'expiration_date')
    search_fields = ('name', 'district_number')


class ConversionFinancialsInline(admin.StackedInline):
    model = ConversionFinancials
    extra = 0
    fieldsets = (
        ('Acquisition', {
            'fields': ('purchase_price', 'purchase_year',
                       'assessed_value_before', 'assessed_value_after')
        }),
        ('Project Cost', {
            'fields': ('rehab_cost_estimate', 'total_project_cost')
        }),
        ('Public Incentives', {
            'fields': ('tif_amount', 'historic_tax_credits', 'nmtc_amount', 'other_incentives')
        }),
        ('Unit Economics', {
            'fields': ('avg_sale_price', 'avg_rent_monthly', 'avg_hoa_monthly',
                       'avg_property_tax_annual')
        }),
        ('Data Quality', {
            'fields': ('data_confidence', 'data_sources', 'notes')
        }),
    )


@admin.register(BuildingConversion)
class BuildingConversionAdmin(admin.ModelAdmin):
    list_display = ('name', 'neighborhood', 'original_building_type', 'status',
                    'original_units', 'original_unit_label', 'residential_units',
                    'completion_year', 'featured', 'published')
    list_filter = ('status', 'original_building_type', 'conversion_type',
                   'unit_type', 'neighborhood', 'featured', 'published')
    search_fields = ('name', 'original_name', 'current_name', 'address', 'developer')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('featured', 'published')
    inlines = [ConversionFinancialsInline]
    fieldsets = (
        ('Building Identity', {
            'fields': ('name', 'slug', 'original_name', 'current_name',
                       'neighborhood', 'tif_district', 'featured', 'published')
        }),
        ('Location', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Conversion Details', {
            'fields': ('original_building_type', 'conversion_type', 'status',
                       'original_units', 'original_unit_label', 'year_built',
                       'residential_units', 'unit_type', 'completion_year')
        }),
        ('Team', {
            'fields': ('developer', 'architect', 'general_contractor')
        }),
        ('Content', {
            'fields': ('description', 'cover_image_url', 'source_url')
        }),
    )


# ---------------------------------------------------------------------------
# SUBSCRIPTION SYSTEM
# ---------------------------------------------------------------------------

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'price_monthly', 'price_annual',
                    'show_financials', 'show_comparables', 'show_powerbi',
                    'api_access', 'highlight', 'order')
    list_editable = ('order', 'highlight')
    list_filter = ('tier',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'interval',
                    'current_period_end', 'created_at')
    list_filter = ('status', 'plan', 'interval')
    search_fields = ('user__email', 'user__username', 'stripe_customer_id')
    readonly_fields = ('created_at', 'updated_at')


# ---------------------------------------------------------------------------
# POWER BI REPORTS
# ---------------------------------------------------------------------------

@admin.register(PowerBIReport)
class PowerBIReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'scope', 'embed_mode', 'min_tier',
                    'building', 'neighborhood', 'featured', 'published')
    list_filter = ('scope', 'embed_mode', 'min_tier', 'featured', 'published')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('featured', 'published')
    fieldsets = (
        ('Report Identity', {
            'fields': ('name', 'slug', 'scope', 'description', 'thumbnail_url',
                       'default_height_px', 'min_tier', 'featured', 'published')
        }),
        ('Linked Content', {
            'fields': ('building', 'neighborhood'),
            'description': 'Attach this report to a specific building or neighborhood (optional).',
        }),
        ('Power BI Identifiers', {
            'fields': ('embed_mode', 'workspace_id', 'report_id', 'dataset_id', 'public_embed_url'),
            'description': (
                'For public reports: paste the full iframe src from Power BI → Share → Publish to web. '
                'For private reports: paste the Workspace ID, Report ID, and Dataset ID from the '
                'report URL (app.powerbi.com/groups/{workspace_id}/reports/{report_id}).'
            ),
        }),
    )
