"""
Django Admin configuration for Missouri Construction ecosystem.
This is YOUR command center - manage all sites, cities, articles, businesses.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Site, City, Article, Business, Event, CityImage, Product, Order, OrderItem, EventSource


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['domain_name', 'display_name', 'site_type', 'is_active', 'city_count', 'article_count']
    list_filter = ['site_type', 'is_active', 'launch_date']
    search_fields = ['domain_name', 'display_name']
    readonly_fields = ['city_count', 'article_count', 'business_count']
    
    fieldsets = [
        ('Site Information', {
            'fields': ['domain_name', 'display_name', 'site_type']
        }),
        ('Branding', {
            'fields': ['primary_color']
        }),
        ('Analytics & Tracking', {
            'fields': ['google_analytics_id', 'is_active', 'launch_date']
        }),
        ('Statistics', {
            'fields': ['city_count', 'article_count', 'business_count'],
            'classes': ['collapse']
        }),
    ]
    
    def city_count(self, obj):
        return obj.cities.count()
    city_count.short_description = 'Cities'
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'
    
    def business_count(self, obj):
        return obj.businesses.count()
    business_count.short_description = 'Businesses'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'country', 'population', 'article_count', 'business_count', 'last_census_updated']
    list_filter = ['country', 'state', 'sites']
    search_fields = ['name', 'state']
    filter_horizontal = ['sites']
    readonly_fields = ['created_at', 'updated_at', 'article_count', 'business_count']
    
    fieldsets = [
        ('Location', {
            'fields': ['name', 'state', 'country', 'latitude', 'longitude']
        }),
        ('Demographics (Census Data)', {
            'fields': ['population', 'median_income', 'census_data', 'last_census_updated']
        }),
        ('Site Association', {
            'fields': ['sites']
        }),
        ('Statistics', {
            'fields': ['article_count', 'business_count', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'
    
    def business_count(self, obj):
        return obj.businesses.count()
    business_count.short_description = 'Businesses'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'city', 'site', 'category', 'published', 'view_count', 'published_date', 'ai_generated']
    list_filter = ['published', 'ai_generated', 'category', 'site', 'featured']
    search_fields = ['title', 'content', 'city__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'share_count', 'last_viewed', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Article Content', {
            'fields': ['title', 'slug', 'excerpt', 'content', 'category']
        }),
        ('Association', {
            'fields': ['city', 'site', 'created_by']
        }),
        ('AI Tracking', {
            'fields': ['ai_generated', 'ai_model_used', 'source_url', 'prompt_used'],
            'classes': ['collapse']
        }),
        ('SEO', {
            'fields': ['meta_description', 'keywords']
        }),
        ('Publishing', {
            'fields': ['published', 'published_date', 'featured']
        }),
        ('Performance (Point of Sale Data)', {
            'fields': ['view_count', 'share_count', 'last_viewed'],
            'classes': ['collapse']
        }),
        ('Meta', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('city', 'site', 'created_by')


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'category', 'tier_badge', 'monthly_cost', 'view_count', 'verified', 'active']
    list_filter = ['tier', 'category', 'verified', 'active', 'site']
    search_fields = ['name', 'city__name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['view_count', 'click_count', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Business Information', {
            'fields': ['name', 'slug', 'category', 'description']
        }),
        ('Location', {
            'fields': ['city', 'site', 'address']
        }),
        ('Contact', {
            'fields': ['phone', 'email', 'website']
        }),
        ('Listing Tier & Revenue', {
            'fields': ['tier', 'monthly_cost', 'subscription_start', 'subscription_end', 'featured_until']
        }),
        ('Premium Features', {
            'fields': ['logo', 'photos'],
            'classes': ['collapse']
        }),
        ('Performance', {
            'fields': ['view_count', 'click_count', 'verified', 'active'],
            'classes': ['collapse']
        }),
        ('Meta', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    
    def tier_badge(self, obj):
        colors = {
            'FREE': 'gray',
            'PREMIUM': 'blue',
            'FEATURED': 'gold'
        }
        color = colors.get(obj.tier, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.tier
        )
    tier_badge.short_description = 'Tier'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'city', 'site', 'start_date', 'ai_scraped', 'organizer']
    list_filter = ['ai_scraped', 'site', 'city']
    search_fields = ['title', 'description', 'city__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = [
        ('Event Information', {
            'fields': ['title', 'slug', 'description']
        }),
        ('Location & Association', {
            'fields': ['city', 'site', 'location', 'organizer']
        }),
        ('Dates', {
            'fields': ['start_date', 'end_date']
        }),
        ('Links', {
            'fields': ['event_url', 'ticket_url']
        }),
        ('AI Tracking', {
            'fields': ['ai_scraped', 'source_url'],
            'classes': ['collapse']
        }),
        ('Meta', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]




@admin.register(CityImage)
class CityImageAdmin(admin.ModelAdmin):
    list_display = ['city', 'uploaded_by', 'caption', 'is_approved', 'ai_flagged', 'uploaded_at']
    list_filter = ['is_approved', 'ai_flagged', 'city']
    search_fields = ['caption', 'ai_description', 'uploaded_by__username']
    readonly_fields = ['ai_description', 'ai_tags', 'ai_flagged', 'uploaded_at']
    actions = ['approve_images', 'reject_images']

    def approve_images(self, request, queryset):
        queryset.update(is_approved=True)
    approve_images.short_description = 'Approve selected photos'

    def reject_images(self, request, queryset):
        queryset.update(is_approved=False)
    reject_images.short_description = 'Reject selected photos'


# ============================================================================
# MARKETPLACE ADMIN
# ============================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'business', 'city', 'current_price', 'category', 'condition',
                    'quantity_available', 'is_active', 'is_approved', 'ai_flagged', 'sold_count']
    list_filter = ['is_active', 'is_approved', 'ai_flagged', 'category', 'condition', 'city']
    search_fields = ['name', 'description', 'business__name']
    readonly_fields = ['sold_count', 'view_count', 'created_at', 'updated_at']
    actions = ['approve_products', 'reject_products']

    def approve_products(self, request, queryset):
        queryset.update(is_approved=True)
    approve_products.short_description = 'Approve selected products (make live)'

    def reject_products(self, request, queryset):
        queryset.update(is_approved=False, is_active=False)
    reject_products.short_description = 'Reject selected products'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'business', 'quantity', 'unit_price', 'subtotal']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer', 'guest_email', 'status', 'total', 'platform_fee', 'created_at']
    list_filter = ['status', 'created_at', 'site']
    search_fields = ['buyer__username', 'guest_email', 'stripe_checkout_session_id']
    readonly_fields = ['stripe_checkout_session_id', 'stripe_payment_intent_id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


# ============================================================================
# CALENDAR ADMIN
# ============================================================================

@admin.register(EventSource)
class EventSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'feed_type', 'is_active', 'last_fetched', 'consecutive_failures', 'last_error_short']
    list_filter = ['feed_type', 'is_active', 'city__state']
    search_fields = ['name', 'feed_url', 'city__name']
    readonly_fields = ['last_fetched', 'last_success', 'consecutive_failures', 'last_error', 'created_at', 'updated_at']
    actions = ['activate_sources', 'deactivate_sources']

    def last_error_short(self, obj):
        if obj.last_error:
            return obj.last_error[:60] + '…' if len(obj.last_error) > 60 else obj.last_error
        return '—'
    last_error_short.short_description = 'Last Error'

    def activate_sources(self, request, queryset):
        queryset.update(is_active=True)
    activate_sources.short_description = 'Activate selected sources'

    def deactivate_sources(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_sources.short_description = 'Deactivate selected sources'


# Customize admin site branding
admin.site.site_header = "Missouri Construction - Master Control"
admin.site.site_title = "MoCon Admin"
admin.site.index_title = "Multi-Site Ecosystem Management"
