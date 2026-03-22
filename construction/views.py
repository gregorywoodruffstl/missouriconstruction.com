from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (Project, ProjectCategory, GalleryImage, BidOpportunity,
                     PermitRecord, Neighborhood, BuildingConversion, ConversionFinancials,
                     SubscriptionPlan, UserSubscription, PowerBIReport)


def home(request):
    featured_projects = Project.objects.filter(featured=True).prefetch_related('images')[:6]
    active_bids = BidOpportunity.objects.filter(status='open').order_by('due_date')[:5]
    recent_permits = PermitRecord.objects.all().order_by('-issued_date')[:8]
    categories = ProjectCategory.objects.all()

    # Busch Stadium III teaser — a specific project if it exists
    busch_stadium = Project.objects.filter(slug='busch-stadium-iii').first()

    context = {
        'featured_projects': featured_projects,
        'active_bids': active_bids,
        'recent_permits': recent_permits,
        'categories': categories,
        'busch_stadium': busch_stadium,
    }
    return render(request, 'construction/home.html', context)


def project_list(request):
    projects = Project.objects.all().prefetch_related('images')
    category_slug = request.GET.get('category')
    status_filter = request.GET.get('status')
    city_filter = request.GET.get('city')

    if category_slug:
        projects = projects.filter(category__slug=category_slug)
    if status_filter:
        projects = projects.filter(status=status_filter)
    if city_filter:
        projects = projects.filter(city__icontains=city_filter)

    categories = ProjectCategory.objects.all()
    context = {
        'projects': projects,
        'categories': categories,
        'current_category': category_slug,
        'current_status': status_filter,
    }
    return render(request, 'construction/project_list.html', context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    images = project.images.all()
    related_projects = Project.objects.filter(
        category=project.category
    ).exclude(pk=project.pk)[:4]

    context = {
        'project': project,
        'images': images,
        'related_projects': related_projects,
    }
    return render(request, 'construction/project_detail.html', context)


def gallery(request):
    """Busch Stadium III construction photo gallery, grouped by date."""
    from itertools import groupby
    busch_project = get_object_or_404(Project, slug='busch-stadium-iii')
    images = busch_project.images.all().order_by('taken_date', 'order', 'pk')
    season_filter = request.GET.get('season')
    if season_filter:
        images = images.filter(season=season_filter)

    # Group images by taken_date so each day becomes its own section
    grouped = []
    for date, day_images in groupby(images, key=lambda img: img.taken_date):
        grouped.append((date, list(day_images)))

    context = {
        'project': busch_project,
        'images': images,
        'grouped_images': grouped,
        'current_season': season_filter,
        'seasons': [('spring', 'Spring'), ('summer', 'Summer'), ('fall', 'Fall'), ('winter', 'Winter')],
    }
    return render(request, 'construction/gallery.html', context)


def bids_list(request):
    open_bids = BidOpportunity.objects.filter(status='open').order_by('due_date')
    closed_bids = BidOpportunity.objects.filter(status__in=['closed', 'awarded']).order_by('-due_date')[:20]

    context = {
        'open_bids': open_bids,
        'closed_bids': closed_bids,
    }
    return render(request, 'construction/bids.html', context)


def permits_list(request):
    permits = PermitRecord.objects.all()
    city_filter = request.GET.get('city')
    type_filter = request.GET.get('type')

    if city_filter:
        permits = permits.filter(city__icontains=city_filter)
    if type_filter:
        permits = permits.filter(permit_type__icontains=type_filter)

    context = {
        'permits': permits,
        'current_city': city_filter,
        'current_type': type_filter,
    }
    return render(request, 'construction/permits.html', context)


def about(request):
    return render(request, 'construction/about.html')


def apprenticeships(request):
    """Trade union apprenticeship programs — connects St. Louis area teens to trade careers."""
    return render(request, 'construction/apprenticeships.html')


def fan_hall_of_fame(request):
    """Cardinals Fan Hall of Fame — the Sunday launch article / open letter."""
    return render(request, 'construction/fan_hall_of_fame.html')


def privacy(request):
    return render(request, 'construction/privacy.html')


def terms(request):
    return render(request, 'construction/terms.html')


def data_deletion(request):
    return render(request, 'construction/data_deletion.html')


# ---------------------------------------------------------------------------
# ST. LOUIS BUILDING CONVERSION ANALYSIS
# ---------------------------------------------------------------------------

def conversion_list(request):
    conversions = (BuildingConversion.objects
                   .filter(published=True)
                   .select_related('neighborhood', 'financials')
                   .order_by('-completion_year', 'neighborhood__name', 'name'))

    neighborhoods = Neighborhood.objects.filter(
        conversions__published=True
    ).distinct().order_by('district', 'name')

    building_type = request.GET.get('type')
    neighborhood_slug = request.GET.get('neighborhood')
    status = request.GET.get('status')

    if building_type:
        conversions = conversions.filter(original_building_type=building_type)
    if neighborhood_slug:
        conversions = conversions.filter(neighborhood__slug=neighborhood_slug)
    if status:
        conversions = conversions.filter(status=status)

    # Summary stats for the page header
    stats = conversions.aggregate(
        total_buildings=Count('id'),
        total_units=Sum('residential_units'),
    )

    context = {
        'conversions': conversions,
        'neighborhoods': neighborhoods,
        'stats': stats,
        'building_types': BuildingConversion.BUILDING_TYPE_CHOICES,
        'status_choices': BuildingConversion.STATUS_CHOICES,
        'active_filters': {
            'type': building_type,
            'neighborhood': neighborhood_slug,
            'status': status,
        },
    }
    return render(request, 'construction/conversion_list.html', context)


def conversion_detail(request, slug):
    conversion = get_object_or_404(
        BuildingConversion.objects.select_related('neighborhood', 'tif_district', 'financials'),
        slug=slug,
        published=True,
    )
    related = (BuildingConversion.objects
               .filter(neighborhood=conversion.neighborhood, published=True)
               .exclude(pk=conversion.pk)[:4])

    # Determine subscriber access level
    user_tier = 'scout'
    if request.user.is_authenticated:
        sub = getattr(request.user, 'subscription', None)
        if sub and sub.is_active:
            user_tier = sub.plan.tier

    show_financials = user_tier in ('analyst', 'professional', 'enterprise')
    show_comparables = user_tier in ('professional', 'enterprise')
    show_powerbi = user_tier in ('professional', 'enterprise')

    # Power BI reports attached to this building — filter to what user can see
    pbi_reports = [
        r for r in conversion.pbi_reports.filter(published=True)
        if r.user_can_view(request.user)
    ]

    context = {
        'conversion': conversion,
        'related': related,
        'user_tier': user_tier,
        'show_financials': show_financials,
        'show_comparables': show_comparables,
        'show_powerbi': show_powerbi,
        'pbi_reports': pbi_reports,
    }
    return render(request, 'construction/conversion_detail.html', context)


def neighborhood_detail(request, slug):
    neighborhood = get_object_or_404(Neighborhood, slug=slug)
    conversions = (BuildingConversion.objects
                   .filter(neighborhood=neighborhood, published=True)
                   .select_related('financials')
                   .order_by('-completion_year'))
    stats = conversions.aggregate(
        total_buildings=Count('id'),
        total_units=Sum('residential_units'),
    )
    context = {
        'neighborhood': neighborhood,
        'conversions': conversions,
        'stats': stats,
    }
    return render(request, 'construction/neighborhood_detail.html', context)


# ---------------------------------------------------------------------------
# Power BI Report Library
# ---------------------------------------------------------------------------

def powerbi_reports(request):
    """
    Citywide Power BI report library — shows all published reports.
    Free users see the report cards but the embed is gated.
    """
    all_reports = PowerBIReport.objects.filter(published=True).order_by('scope', 'name')

    # Tag each report with whether the current user can view it
    reports_with_access = [
        (report, report.user_can_view(request.user))
        for report in all_reports
    ]

    # Featured citywide reports for the top section
    featured_reports = [
        (r, can_view) for r, can_view in reports_with_access
        if r.featured
    ]

    context = {
        'reports_with_access': reports_with_access,
        'featured_reports': featured_reports,
    }
    return render(request, 'construction/powerbi_reports.html', context)


# ---------------------------------------------------------------------------
# Subscription Views
# ---------------------------------------------------------------------------

def subscription_plans(request):
    """Public pricing page — no login required."""
    plans = SubscriptionPlan.objects.all().order_by('order')

    current_plan = None
    if request.user.is_authenticated:
        sub = getattr(request.user, 'subscription', None)
        if sub and sub.is_active:
            current_plan = sub.plan.tier

    context = {
        'plans': plans,
        'current_plan': current_plan,
    }
    return render(request, 'construction/subscription_plans.html', context)


@login_required
def my_subscription(request):
    """Subscriber dashboard showing current plan and usage."""
    sub = getattr(request.user, 'subscription', None)
    context = {
        'subscription': sub,
        'plans': SubscriptionPlan.objects.all().order_by('order'),
    }
    return render(request, 'construction/my_subscription.html', context)


@login_required
def subscribe_plan(request, tier):
    """
    Initiate subscription checkout for a given tier.
    Currently a placeholder — Stripe Checkout integration goes here.
    """
    plan = get_object_or_404(SubscriptionPlan, tier=tier)

    if plan.is_free:
        # Free Scout tier — assign immediately
        sub, created = UserSubscription.objects.get_or_create(
            user=request.user,
            defaults={'plan': plan, 'status': 'active'},
        )
        if not created:
            sub.plan = plan
            sub.status = 'active'
            sub.save()
        messages.success(request, f"You're now on the {plan.name} plan.")
        return redirect('construction:my_subscription')

    # Paid tier → would hand off to Stripe Checkout here
    # TODO: create Stripe Checkout session and redirect to stripe
    messages.info(
        request,
        f"Stripe payment for {plan.name} (${plan.price_monthly}/mo) "
        f"is coming soon — contact us to subscribe early."
    )
    return redirect('construction:subscription_plans')
