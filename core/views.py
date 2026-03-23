"""
Core Views - City Pages and Articles

These views serve the public-facing website using the templates we built.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from .models import Site, City, Article, Business, UserProfile, BusinessReview, Bookmark, CityImage, Product, Order, OrderItem, Event, EventSource
from .weather_api import get_current_weather, get_5_day_forecast
from .sports_api import get_local_sports_teams, get_recent_sports_news
from .grokipedia_api import get_famous_people_from_city
from .vision_api import analyze_image
from .forms import CitizenSignupForm, CustomLoginForm, ProfileEditForm, BusinessSignupForm
from .news_api import fetch_city_news, fetch_city_topic_news, has_city_topics
from .hotel_affiliate import get_hotel_links


def home(request):
    """
    Homepage - Welcome to Seeking Springfield!
    Shows all 22 Springfield cities with stats
    """
    
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    
    # Get all Springfield cities with their article counts
    cities = City.objects.filter(
        sites=site
    ).prefetch_related('articles', 'state').order_by('state__abbreviation', 'name')
    
    # Add stats to each city
    cities_with_stats = []
    for city in cities:
        cities_with_stats.append({
            'city': city,
            'article_count': city.articles.filter(published=True).count(),
            'population': city.population or 'N/A',
        })
    
    # Get latest articles across all cities
    latest_articles = Article.objects.filter(
        published=True,
        site=site
    ).select_related('city', 'city__state').order_by('-published_date')[:6]
    
    # Calculate total stats
    total_cities = cities.count()
    total_articles = Article.objects.filter(site=site, published=True).count()
    total_businesses = Business.objects.filter(active=True).count()
    
    context = {
        'site': site,
        'cities_with_stats': cities_with_stats,
        'latest_articles': latest_articles,
        'total_cities': total_cities,
        'total_articles': total_articles,
        'total_businesses': total_businesses,
    }
    
    return render(request, 'base/home.html', context)


def city_home(request, state, city_slug):
    """
    City homepage with demographics, weather, famous people, sports
    USER REQUESTED: All API integrations (Weather, Sports, Grokipedia)
    """
    
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    
    # Get city
    city = get_object_or_404(City, name__iexact=city_slug.replace('-', ' '), state__abbreviation__iexact=state)
    
    # Get articles for this city
    articles = Article.objects.filter(
        city=city,
        published=True
    ).order_by('-published_date')[:10]
    
    # Get businesses for this city
    businesses = Business.objects.filter(
        city=city,
        active=True
    ).order_by('-tier', '-view_count')[:6]
    
    # Get other cities with same name (for "Seeking" sites)
    other_cities = None
    if site and 'seeking' in site.domain_name.lower():
        other_cities = City.objects.filter(
            name=city.name,
            sites=site
        ).exclude(id=city.id).order_by('-population')
    
    # API INTEGRATIONS (USER REQUESTED)
    
    # 1. Weather — loaded async via /api/weather/ endpoint (non-blocking)
    #    See weather_json() view below — keeps API key server-side and cached.

    # 2. Sports Teams and News (ESPN RSS)
    sports_teams = get_local_sports_teams(city.name, city.state.name) if city.state else []
    sports_news = get_recent_sports_news(city.name, city.state.name, limit=5) if city.state else []
    
    # 3. Famous People (Grokipedia - NEXT LEVEL!)
    famous_people = get_famous_people_from_city(city.name, city.state.name, limit=8) if city.state else []

    # 4. City Image Gallery
    gallery_images = CityImage.objects.filter(
        city=city, is_approved=True, ai_flagged=False
    ).select_related('uploaded_by').order_by('-uploaded_at')[:24]

    # 5. Local News (Google News RSS — no API key required, cached 30 min)
    city_news = fetch_city_news(city, max_results=8)
    topic_news = fetch_city_topic_news(city, max_results_per_topic=4)
    city_has_topics = has_city_topics(city)

    # 6. Hotel affiliate links (commissions from Expedia / Booking.com / chains)
    hotel_links = get_hotel_links(city)

    context = {
        'site': site,
        'city': city,
        'articles': articles,
        'businesses': businesses,
        'other_cities': other_cities,
        # API data — weather loaded client-side via /api/weather/ endpoint
        'sports_teams': sports_teams,
        'sports_news': sports_news,
        'famous_people': famous_people,
        # Gallery
        'gallery_images': gallery_images,
        # News
        'city_news': city_news,
        'topic_news': topic_news,
        'city_has_topics': city_has_topics,
        # Hotels
        'hotel_links': hotel_links,
    }
    
    return render(request, 'base/city_home.html', context)


def article_detail(request, slug):
    """Individual article page"""
    
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    
    # Get article
    article = get_object_or_404(Article, slug=slug, published=True)
    
    # Record view (Point of Sale tracking!)
    article.record_view()
    
    # Get related articles (same city, different category)
    related_articles = Article.objects.filter(
        city=article.city,
        published=True
    ).exclude(id=article.id).order_by('-published_date')[:4]
    
    context = {
        'site': site,
        'article': article,
        'related_articles': related_articles,
    }
    
    return render(request, 'base/article.html', context)


def weather_json(request, state, city_slug):
    """
    JSON endpoint for weather data — called asynchronously by the city page JS.
    Keeps the API key server-side and caches responses for 10 minutes.
    Returns both current weather and 5-day forecast in one call.
    """
    city = get_object_or_404(City, slug=city_slug, state__abbreviation__iexact=state)
    state_abbr = city.state.abbreviation if city.state else ''

    current = get_current_weather(city.name, state_abbr) if state_abbr else None
    forecast = get_5_day_forecast(city.name, state_abbr) if state_abbr else []

    # Convert date objects to strings for JSON serialisation
    forecast_clean = []
    for day in forecast:
        d = dict(day)
        if hasattr(d.get('date'), 'strftime'):
            d['date'] = d['date'].strftime('%m/%d')
        forecast_clean.append(d)

    return JsonResponse({
        'current': current,
        'forecast': forecast_clean,
    })


@require_POST
@csrf_exempt  # Remove this in production - use proper CSRF
def article_view_api(request, article_id):
    """API endpoint to record article view via AJAX"""
    
    try:
        article = Article.objects.get(id=article_id, published=True)
        article.record_view()
        
        return JsonResponse({
            'success': True,
            'view_count': article.view_count
        })
    except Article.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Article not found'
        }, status=404)


# ============================================================================
# AUTHENTICATION VIEWS (Citizens First Strategy!)
# ============================================================================

def signup_view(request):
    """
    Citizen Signup (FREE)
    
    Part of "Citizens First" strategy:
    1. Citizens register FREE
    2. See value in the platform
    3. Tell their boss
    4. Boss pays for Premium
    """
    
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = CitizenSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send verification email
            send_verification_email(user)
            
            # Auto-login after signup
            login(request, user)
            
            messages.success(request, '🎉 Welcome! Check your email to verify your account.')
            return redirect('profile')
    else:
        form = CitizenSignupForm()
    
    # Get all cities for dropdown (alphabetically by state)
    cities = City.objects.select_related('state').order_by('state__name', 'name')
    
    context = {
        'form': form,
        'cities': cities,
    }
    
    return render(request, 'auth/signup.html', context)


def login_view(request):
    """
    User Login (supports username or email)
    """
    
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session expiry (remember me = 30 days, else browser session)
                if remember_me:
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
                else:
                    request.session.set_expiry(0)  # Browser close
                
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                # Redirect to next page or profile
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
    else:
        form = CustomLoginForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'auth/login.html', context)


def logout_view(request):
    """User Logout"""
    logout(request)
    messages.success(request, 'You have been logged out. Come back soon!')
    return redirect('home')


@login_required
def profile_view(request):
    """
    User Profile Page
    
    Shows:
    - Activity stats (reviews, bookmarks, comments)
    - Bookmarks (businesses, articles, events)
    - My reviews
    - My businesses (if business owner)
    """
    
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Get active tab from query param
    active_tab = request.GET.get('tab', 'bookmarks')
    
    # Get user's bookmarks
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')
    
    # Get user's reviews
    reviews = BusinessReview.objects.filter(user=request.user).order_by('-created_at')
    
    # Get businesses user manages (if business owner)
    managed_businesses = []
    if profile.user_type == 'BUSINESS':
        managed_businesses = Business.objects.filter(managers=request.user)
    
    context = {
        'profile': profile,
        'active_tab': active_tab,
        'bookmarks': bookmarks,
        'reviews': reviews,
        'managed_businesses': managed_businesses,
    }
    
    return render(request, 'user/profile.html', context)


@login_required
def edit_profile_view(request):
    """
    Edit User Profile
    """
    
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '✓ Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
    }
    
    return render(request, 'user/edit_profile.html', context)


def business_signup_view(request):
    """
    Business Owner Signup (PAID - 30-day FREE trial)
    
    Creates user account AND first business listing
    """
    
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account. Upgrade to Premium from your profile.')
        return redirect('profile')
    
    if request.method == 'POST':
        form = BusinessSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Send verification email
            send_verification_email(user)
            
            # Auto-login
            login(request, user)
            
            # Redirect to create first business
            messages.success(request, '🎉 Welcome to Premium! Let\'s add your first business.')
            return redirect('add_business')
    else:
        form = BusinessSignupForm()
    
    # Get all cities
    cities = City.objects.select_related('state').order_by('state__name', 'name')
    
    context = {
        'form': form,
        'cities': cities,
    }
    
    return render(request, 'auth/business_signup.html', context)


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================

def send_verification_email(user):
    """
    Send email verification link
    
    USER REQUESTED: Email link verification (not postcard or phone)
    """
    
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Generate verification token
    token = get_random_string(length=64)
    profile.email_verification_token = token
    profile.save()
    
    # Build verification URL
    verification_url = f"{settings.SITE_URL}/verify-email/{token}/"
    
    # Send email
    subject = f"Verify your {settings.SITE_NAME} account"
    message = f"""
Hi {user.first_name},

Thanks for signing up for {settings.SITE_NAME}!

Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create this account, you can safely ignore this email.

Best regards,
The {settings.SITE_NAME} Team
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def verify_email_view(request, token):
    """
    Verify email with token from link
    """
    
    try:
        profile = UserProfile.objects.get(email_verification_token=token)
        
        # Check if already verified
        if profile.email_verified:
            messages.info(request, 'Your email is already verified!')
            return redirect('profile')
        
        # Verify the email
        profile.email_verified = True
        profile.email_verified_at = datetime.now()
        profile.email_verification_token = ''  # Clear token
        profile.save()
        
        messages.success(request, '✓ Email verified! You now have full access to all features.')
        return redirect('profile')
        
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('home')


@login_required
def resend_verification_view(request):
    """
    Resend email verification link
    """
    
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.email_verified:
        messages.info(request, 'Your email is already verified!')
        return redirect('profile')
    
    # Send new verification email
    send_verification_email(request.user)
    
    messages.success(request, '✓ Verification email sent! Check your inbox.')
    return redirect('profile')


# Placeholder for password reset (use Django's built-in views)
from django.contrib.auth import views as auth_views


@login_required
def upload_city_image(request, state, city_slug):
    """Upload a photo to a city's gallery. Runs GPT-4o Vision on the saved blob URL."""
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    city = get_object_or_404(City, name__iexact=city_slug.replace('-', ' '), state__abbreviation__iexact=state)
    ctx = {'city': city, 'state': state, 'city_slug': city_slug, 'site': site}

    if request.method == 'POST':
        image_file = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()[:255]

        if not image_file:
            messages.error(request, 'Please select an image to upload.')
            return render(request, 'city/upload_image.html', ctx)

        # Enforce 10 MB limit server-side
        if image_file.size > 10 * 1024 * 1024:
            messages.error(request, 'Image must be 10 MB or smaller.')
            return render(request, 'city/upload_image.html', ctx)

        # Save to Azure Blob Storage via ImageField
        city_image = CityImage(city=city, uploaded_by=request.user, caption=caption)
        city_image.image.save(image_file.name, image_file, save=True)

        # Run AI Vision on the public blob URL
        try:
            public_url = city_image.image.url
            result = analyze_image(public_url)
            city_image.ai_description = result['description']
            city_image.ai_tags = result['tags']
            city_image.ai_flagged = result['flagged']
            if result['flagged']:
                city_image.is_approved = False
            city_image.save()
        except Exception:
            pass  # Vision failure never blocks the upload

        messages.success(request, 'Photo uploaded successfully!')
        return redirect('city_home', state=state, city_slug=city_slug)

    return render(request, 'city/upload_image.html', ctx)


# ============================================================================
# MARKETPLACE VIEWS
# Browse → Product Detail → Stripe Checkout → Order Confirmation
# ============================================================================

def marketplace_home(request):
    """Browse all approved, active products across all cities."""
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()

    category = request.GET.get('category', '')
    city_filter = request.GET.get('city', '')
    q = request.GET.get('q', '').strip()

    products = Product.objects.filter(
        site=site, is_active=True, is_approved=True, quantity_available__gt=0
    ).select_related('business', 'city', 'city__state')

    if category:
        products = products.filter(category=category)
    if city_filter:
        products = products.filter(city__name__icontains=city_filter)
    if q:
        products = products.filter(name__icontains=q) | products.filter(description__icontains=q)

    products = products.order_by('-created_at')

    context = {
        'site': site,
        'products': products,
        'category': category,
        'city_filter': city_filter,
        'q': q,
        'categories': Product.CATEGORY_CHOICES,
    }
    return render(request, 'marketplace/home.html', context)


def product_detail(request, slug):
    """Individual product page with buy button."""
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()

    product = get_object_or_404(Product, slug=slug, is_active=True, is_approved=True, site=site)
    product.view_count += 1
    product.save(update_fields=['view_count'])

    # Related products from the same business
    related = Product.objects.filter(
        business=product.business, is_active=True, is_approved=True
    ).exclude(id=product.id)[:4]

    context = {
        'site': site,
        'product': product,
        'related': related,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'marketplace/product_detail.html', context)


@login_required
def add_product(request):
    """Business owner lists a new product for sale."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.user_type != 'BUSINESS':
        messages.error(request, 'Only registered businesses can list products.')
        return redirect('marketplace_home')

    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    managed_businesses = Business.objects.filter(managers=request.user, active=True)

    if not managed_businesses.exists():
        messages.error(request, 'You need an active business listing before adding products.')
        return redirect('add_business')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price_raw = request.POST.get('price', '0')
        sale_price_raw = request.POST.get('sale_price', '').strip()
        category = request.POST.get('category', 'OTHER')
        condition = request.POST.get('condition', 'NEW')
        quantity = request.POST.get('quantity', 1)
        business_id = request.POST.get('business_id')
        image_file = request.FILES.get('image')

        # Basic validation
        if not name or not description:
            messages.error(request, 'Name and description are required.')
        else:
            try:
                price = Decimal(price_raw)
                sale_price = Decimal(sale_price_raw) if sale_price_raw else None
                business = get_object_or_404(Business, id=business_id, managers=request.user)

                base_slug = slugify(name)
                slug = base_slug
                counter = 1
                while Product.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                product = Product.objects.create(
                    business=business,
                    city=business.city,
                    site=site,
                    name=name,
                    slug=slug,
                    description=description,
                    price=price,
                    sale_price=sale_price,
                    category=category,
                    condition=condition,
                    quantity_available=int(quantity),
                    is_active=True,
                    is_approved=False,  # Requires admin approval
                )

                if image_file:
                    product.primary_image.save(image_file.name, image_file, save=True)

                messages.success(request, 'Product submitted! It will appear in the marketplace once approved by our team (usually within 24 hours).')
                return redirect('marketplace_home')
            except Exception as e:
                messages.error(request, f'Error creating product: {e}')

    context = {
        'site': site,
        'managed_businesses': managed_businesses,
        'categories': Product.CATEGORY_CHOICES,
        'conditions': Product.CONDITION_CHOICES,
    }
    return render(request, 'marketplace/add_product.html', context)


def create_checkout_session(request, product_id):
    """
    Create a Stripe Checkout Session for a single product purchase.
    Redirect the user to Stripe's hosted checkout page.
    Platform takes MARKETPLACE_FEE_PERCENT percent.
    """
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY

    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    product = get_object_or_404(Product, id=product_id, is_active=True, is_approved=True)

    if product.quantity_available < 1:
        messages.error(request, 'Sorry, this item is sold out.')
        return redirect('product_detail', slug=product.slug)

    fee_percent = getattr(settings, 'MARKETPLACE_FEE_PERCENT', 10)
    unit_price_cents = int(product.current_price * 100)  # Stripe works in cents

    site_url = settings.SITE_URL.rstrip('/')

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': unit_price_cents,
                    'product_data': {
                        'name': product.name,
                        'description': product.description[:500],
                        'images': [product.hero_image_url] if product.hero_image_url else [],
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{site_url}/marketplace/order/success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{site_url}/marketplace/product/{product.slug}/",
            metadata={
                'product_id': str(product.id),
                'site_id': str(site.id) if site else '',
                'buyer_id': str(request.user.id) if request.user.is_authenticated else '',
            },
            # Collect shipping address
            shipping_address_collection={
                'allowed_countries': ['US'],
            },
        )

        # Create a PENDING order record
        order = Order.objects.create(
            buyer=request.user if request.user.is_authenticated else None,
            guest_email='',
            stripe_checkout_session_id=session.id,
            status='PENDING',
            subtotal=product.current_price,
            platform_fee=(product.current_price * Decimal(fee_percent) / 100),
            total=product.current_price,
            site=site,
        )
        OrderItem.objects.create(
            order=order,
            product=product,
            business=product.business,
            quantity=1,
            unit_price=product.current_price,
        )

        return redirect(session.url, code=303)

    except stripe.error.StripeError as e:
        messages.error(request, f'Payment system error: {e.user_message}')
        return redirect('product_detail', slug=product.slug)


@csrf_exempt
def stripe_marketplace_webhook(request):
    """
    Stripe sends a POST here when a checkout session completes.
    We mark the order PAID and decrement product inventory.
    """
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = settings.STRIPE_MARKETPLACE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        _fulfill_order(session)

    return HttpResponse(status=200)


def _fulfill_order(session):
    """Internal helper — mark order paid, reduce inventory."""
    session_id = session.get('id')
    try:
        order = Order.objects.get(stripe_checkout_session_id=session_id)
    except Order.DoesNotExist:
        return

    if order.status != 'PENDING':
        return  # Already processed (idempotency)

    # Update order
    order.stripe_payment_intent_id = session.get('payment_intent', '')
    order.status = 'PAID'
    # Capture shipping details if provided
    shipping = session.get('shipping_details') or {}
    order.shipping_name = shipping.get('name', '')
    order.shipping_address = shipping.get('address', {})
    if not order.buyer and session.get('customer_details'):
        order.guest_email = session['customer_details'].get('email', '')
    order.save()

    # Reduce quantity for each item
    for item in order.items.select_related('product'):
        product = item.product
        if product.quantity_available >= item.quantity:
            product.quantity_available -= item.quantity
            product.sold_count += item.quantity
            product.save(update_fields=['quantity_available', 'sold_count'])


def order_success(request):
    """
    Order confirmation page shown after successful Stripe checkout.
    """
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    session_id = request.GET.get('session_id', '')

    order = None
    if session_id:
        order = Order.objects.filter(
            stripe_checkout_session_id=session_id
        ).prefetch_related('items__product', 'items__business').first()

    context = {
        'site': site,
        'order': order,
    }
    return render(request, 'marketplace/order_success.html', context)


# ============================================================================
# BUSINESS DETAIL VIEW (with Census + Traffic data)
# ============================================================================

def business_detail(request, business_id):
    """
    Full business profile page with:
    - Contact info, reviews, photos
    - Census demographics for the city
    - US DOT Annual Average Daily Traffic (AADT) estimate for the area
    - Products listed for sale (if any)
    """
    from .census_api import get_city_demographics
    try:
        from .dot_traffic_api import get_city_traffic_data
    except ImportError:
        get_city_traffic_data = None

    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()

    business = get_object_or_404(Business, id=business_id, active=True)
    business.view_count += 1
    business.save(update_fields=['view_count'])

    reviews = BusinessReview.objects.filter(
        business=business, approved=True
    ).select_related('user').order_by('-created_at')

    products = Product.objects.filter(
        business=business, is_active=True, is_approved=True, quantity_available__gt=0
    ).order_by('-created_at')[:8]

    # Census demographics
    census_data = None
    try:
        census_data = get_city_demographics(
            business.city.name,
            business.city.state.abbreviation if business.city.state else ''
        )
    except Exception:
        pass

    # Traffic data
    traffic_data = None
    if get_city_traffic_data:
        try:
            traffic_data = get_city_traffic_data(
                business.city.name,
                business.city.state.abbreviation if business.city.state else ''
            )
        except Exception:
            pass

    context = {
        'site': site,
        'business': business,
        'reviews': reviews,
        'products': products,
        'census_data': census_data,
        'traffic_data': traffic_data,
    }
    return render(request, 'city/business_detail.html', context)


# ── Municipal Calendar Views ───────────────────────────────────────────────

def city_events(request, state, city_slug):
    """Events for a single Springfield city, filterable by date range."""
    site = Site.objects.filter(domain_name=request.get_host()).first()
    city = get_object_or_404(City, slug=city_slug, state__abbreviation__iexact=state)

    # Date filtering – default to next 30 days
    today = timezone.now().date()
    date_from_raw = request.GET.get('from')
    date_to_raw = request.GET.get('to')
    try:
        date_from = datetime.strptime(date_from_raw, '%Y-%m-%d').date() if date_from_raw else today
    except ValueError:
        date_from = today
    try:
        date_to = datetime.strptime(date_to_raw, '%Y-%m-%d').date() if date_to_raw else today + timedelta(days=30)
    except ValueError:
        date_to = today + timedelta(days=30)

    events = (
        Event.objects
        .filter(city=city, start_date__date__gte=date_from, start_date__date__lte=date_to)
        .order_by('start_date')
        .select_related('source')
    )

    context = {
        'site': site,
        'city': city,
        'events': events,
        'date_from': date_from,
        'date_to': date_to,
        'today': today,
    }
    return render(request, 'city/events.html', context)


def master_calendar(request):
    """Cross-city calendar — all 22 Springfields, filterable by state/date."""
    site = Site.objects.filter(domain_name=request.get_host()).first()
    today = timezone.now().date()

    # Filters
    state_filter = request.GET.get('state', '')
    date_from_raw = request.GET.get('from')
    date_to_raw = request.GET.get('to')
    try:
        date_from = datetime.strptime(date_from_raw, '%Y-%m-%d').date() if date_from_raw else today
    except ValueError:
        date_from = today
    try:
        date_to = datetime.strptime(date_to_raw, '%Y-%m-%d').date() if date_to_raw else today + timedelta(days=7)
    except ValueError:
        date_to = today + timedelta(days=7)

    qs = Event.objects.filter(
        start_date__date__gte=date_from,
        start_date__date__lte=date_to,
    ).order_by('start_date').select_related('city', 'city__state', 'source')

    if state_filter:
        qs = qs.filter(city__state__abbreviation__iexact=state_filter)

    # Group events by date for template rendering
    from collections import defaultdict
    events_by_date = defaultdict(list)
    for ev in qs:
        events_by_date[ev.start_date.date()].append(ev)

    # Build sorted list of (date, events) pairs
    grouped = sorted(events_by_date.items())

    # Distinct states for the filter dropdown
    states = (
        City.objects.filter(events__isnull=False)
        .values_list('state__abbreviation', 'state__name')
        .distinct()
        .order_by('state__abbreviation')
    )

    context = {
        'site': site,
        'grouped': grouped,
        'date_from': date_from,
        'date_to': date_to,
        'today': today,
        'state_filter': state_filter,
        'states': states,
    }
    return render(request, 'base/master_calendar.html', context)


def cities_list(request):
    """All Springfield cities across all 22 states."""
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    cities = City.objects.filter(
        sites=site
    ).exclude(name='').prefetch_related('state').order_by('state__abbreviation', 'name')
    return render(request, 'base/cities_list.html', {'site': site, 'cities': cities})


def article_list(request):
    """All published articles across all Springfields."""
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    state_filter = request.GET.get('state', '')
    articles = Article.objects.filter(published=True, site=site).select_related('city', 'city__state').order_by('-published_date')
    if state_filter:
        articles = articles.filter(city__state__abbreviation__iexact=state_filter)
    from django.db.models import Q
    states = City.objects.filter(sites=site).values_list('state__abbreviation', 'state__name').distinct().order_by('state__abbreviation')
    return render(request, 'base/article_list.html', {
        'site': site,
        'articles': articles[:60],
        'states': states,
        'state_filter': state_filter,
    })


def business_directory(request):
    """Business directory across all Springfields."""
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    state_filter = request.GET.get('state', '')
    category_filter = request.GET.get('category', '')
    businesses = Business.objects.filter(active=True).select_related('city', 'city__state').order_by('-tier', 'name')
    if state_filter:
        businesses = businesses.filter(city__state__abbreviation__iexact=state_filter)
    if category_filter:
        businesses = businesses.filter(category__icontains=category_filter)
    states = City.objects.filter(sites=site).values_list('state__abbreviation', 'state__name').distinct().order_by('state__abbreviation')
    categories = Business.objects.filter(active=True).values_list('category', flat=True).distinct().order_by('category')
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(
        start_date__date__gte=today,
    ).order_by('start_date').select_related('city', 'city__state')[:6]
    return render(request, 'base/business_directory.html', {
        'site': site,
        'businesses': businesses[:100],
        'states': states,
        'categories': [c for c in categories if c],
        'state_filter': state_filter,
        'category_filter': category_filter,
        'upcoming_events': upcoming_events,
    })


def about(request):
    """About Seeking Springfield."""
    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()
    today = timezone.now().date()
    upcoming_events = Event.objects.filter(
        start_date__date__gte=today,
    ).order_by('start_date').select_related('city', 'city__state')[:4]
    return render(request, 'base/about.html', {'site': site, 'upcoming_events': upcoming_events})


def cardinals_schedule(request):
    """
    Accessible St. Louis Cardinals monthly schedule.

    MLB.com's official schedule uses color alone to distinguish home/away/spring
    training games, which fails WCAG 2.1 SC 1.4.1 (Use of Color) and is
    unreadable in high contrast and dark mode.

    This view fetches live data from the public MLB Stats API (no key required)
    and renders a calendar that uses text labels (H / A / ST / EX) alongside
    color so it works for all users regardless of display settings.

    Cardinals team ID: 138
    Busch Stadium venue ID: 2889
    """
    import urllib.request as _url_req
    import json as _json
    import calendar as _cal
    from datetime import date as _date

    today = _date.today()

    # Month/year from query string, default to current month
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        if month < 1:
            month = 12
            year -= 1
        if month > 12:
            month = 1
            year += 1
        year = max(2024, min(2030, year))
    except (ValueError, TypeError):
        year, month = today.year, today.month

    # Prev / next month navigation
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    _, last_day = _cal.monthrange(year, month)
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    # MLB Stats API — public endpoint, no auth required
    api_url = (
        f"https://statsapi.mlb.com/api/v1/schedule"
        f"?teamId=138&startDate={start_date}&endDate={end_date}"
        f"&sportId=1&hydrate=team,venue"
    )

    games_by_date = {}
    api_error = False
    try:
        req = _url_req.Request(api_url, headers={'User-Agent': 'SeekingSpringfield/1.0'})
        with _url_req.urlopen(req, timeout=6) as resp:
            data = _json.loads(resp.read().decode())

        for date_entry in data.get('dates', []):
            date_str = date_entry['date']
            day_games = []
            for game in date_entry.get('games', []):
                home = game['teams']['home']['team']
                away = game['teams']['away']['team']
                is_home = home.get('id') == 138
                opponent_name = away.get('teamName', '') if is_home else home.get('teamName', '')
                opponent_abbr = away.get('abbreviation', '') if is_home else home.get('abbreviation', '')
                game_type = game.get('gameType', 'R')  # R=Regular, S=Spring, E=Exhibition

                # Convert UTC game time to Central (CDT=UTC-5 for March-October)
                game_time_ct = ''
                game_date_utc = game.get('gameDate', '')
                if game_date_utc and 'T' in game_date_utc:
                    t = game_date_utc.split('T')[1].rstrip('Z')
                    parts = t.split(':')
                    h_utc, m_utc = int(parts[0]), int(parts[1])
                    h_ct = (h_utc - 5) % 24  # CDT offset
                    ampm = 'PM' if h_ct >= 12 else 'AM'
                    h12 = h_ct % 12 or 12
                    game_time_ct = f"{h12}:{m_utc:02d} {ampm} CT"

                status = game.get('status', {}).get('abstractGameState', '')
                score = ''
                if status == 'Final':
                    h_score = game['teams']['home'].get('score', 0)
                    a_score = game['teams']['away'].get('score', 0)
                    stl_score = h_score if is_home else a_score
                    opp_score = a_score if is_home else h_score
                    if game.get('isTie'):
                        score = f"T {stl_score}-{opp_score}"
                    elif (game['teams']['home'].get('isWinner') and is_home) or \
                         (game['teams']['away'].get('isWinner') and not is_home):
                        score = f"W {stl_score}-{opp_score}"
                    else:
                        score = f"L {stl_score}-{opp_score}"

                day_games.append({
                    'is_home': is_home,
                    'opponent': opponent_name,
                    'opponent_abbr': opponent_abbr,
                    'time': game_time_ct,
                    'game_type': game_type,
                    'status': status,
                    'score': score,
                })
            games_by_date[date_str] = day_games
    except Exception:
        api_error = True

    # Build Sunday-first calendar weeks with game data embedded
    sunday_cal = _cal.Calendar(firstweekday=6)
    weeks = []
    for week in sunday_cal.monthdayscalendar(year, month):
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)
            else:
                d_str = f"{year}-{month:02d}-{day:02d}"
                week_days.append({
                    'day': day,
                    'date_str': d_str,
                    'is_today': (day == today.day and month == today.month and year == today.year),
                    'games': games_by_date.get(d_str, []),
                })
        weeks.append(week_days)

    domain = request.get_host()
    site = Site.objects.filter(domain_name=domain, is_active=True).first()

    return render(request, 'base/cardinals_schedule.html', {
        'site': site,
        'year': year,
        'month': month,
        'month_name': _cal.month_name[month],
        'weeks': weeks,
        'today': today,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'api_error': api_error,
    })

