"""
Core URL Configuration - Public-facing city and article pages
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # City image upload: /il/springfield/upload/
    path('<str:state>/<slug:city_slug>/upload/', views.upload_city_image, name='upload_city_image'),

    # City homepage: /il/springfield/
    path('<str:state>/<slug:city_slug>/', views.city_home, name='city_home'),

    # Article detail: /article/springfield-il-city-guide/
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),

    # API endpoint for article view tracking
    path('api/articles/<int:article_id>/view/', views.article_view_api, name='article_view_api'),

    # Weather JSON endpoint (async — called by city page JavaScript)
    path('api/weather/<str:state>/<slug:city_slug>/', views.weather_json, name='weather_json'),

    # ============================================================================
    # AUTHENTICATION URLS (Citizens First Strategy!)
    # ============================================================================

    # Citizen Registration (FREE)
    path('signup/', views.signup_view, name='signup'),

    # Business Owner Registration (PAID - 30-day trial)
    path('business/signup/', views.business_signup_view, name='business_signup'),

    # Login/Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # User Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # Email Verification
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),

    # Password Reset (Django built-in views)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),
         name='password_reset_complete'),

    # ============================================================================
    # MARKETPLACE URLS
    # ============================================================================

    # Browse all products
    path('marketplace/', views.marketplace_home, name='marketplace_home'),

    # Individual product page
    path('marketplace/product/<slug:slug>/', views.product_detail, name='product_detail'),

    # List a new product (business owner only)
    path('marketplace/add/', views.add_product, name='add_product'),

    # Stripe checkout — create session and redirect to Stripe
    path('marketplace/checkout/<int:product_id>/', views.create_checkout_session, name='create_checkout_session'),

    # Stripe webhook (POST only, no CSRF)
    path('marketplace/webhook/stripe/', views.stripe_marketplace_webhook, name='stripe_marketplace_webhook'),

    # Order confirmation
    path('marketplace/order/success/', views.order_success, name='order_success'),

    # ============================================================================
    # BUSINESS DETAIL URL
    # ============================================================================
    path('business/<int:business_id>/', views.business_detail, name='business_detail'),

    # ============================================================================
    # CALENDAR URLS
    # ============================================================================
    # Master calendar — all 22 Springfields: /events/
    path('events/', views.master_calendar, name='master_calendar'),
    # City-specific calendar: /il/springfield/events/
    path('<str:state>/<slug:city_slug>/events/', views.city_events, name='city_events'),

    # ============================================================================
    # NAV PAGES
    # ============================================================================
    path('cities/', views.cities_list, name='cities_list'),
    path('articles/', views.article_list, name='article_list'),
    path('businesses/', views.business_directory, name='business_directory'),
    path('about/', views.about, name='about'),

    # ============================================================================
    # ACCESSIBLE CARDINALS SCHEDULE
    # WCAG 2.1 SC 1.4.1 compliant — text labels used alongside color indicators
    # MLB.com's official schedule fails this criterion in high contrast / dark mode
    # ============================================================================
    path('cardinals-schedule/', views.cardinals_schedule, name='cardinals_schedule'),
]
