from django.urls import path
from . import views

app_name = 'construction'

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('bids/', views.bids_list, name='bids_list'),
    path('permits/', views.permits_list, name='permits_list'),
    path('about/', views.about, name='about'),
    path('apprenticeships/', views.apprenticeships, name='apprenticeships'),
    path('cardinals-fan-hall-of-fame/', views.fan_hall_of_fame, name='fan_hall_of_fame'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('data-deletion/', views.data_deletion, name='data_deletion'),
    # STL Building Conversion Analysis
    path('stl-conversions/', views.conversion_list, name='conversion_list'),
    path('stl-conversions/neighborhood/<slug:slug>/', views.neighborhood_detail, name='neighborhood_detail'),
    path('stl-conversions/<slug:slug>/', views.conversion_detail, name='conversion_detail'),
    # Power BI Report Library
    path('reports/', views.powerbi_reports, name='powerbi_reports'),
    # Subscription
    path('subscribe/', views.subscription_plans, name='subscription_plans'),
    path('subscribe/<str:tier>/', views.subscribe_plan, name='subscribe_plan'),
    path('my-subscription/', views.my_subscription, name='my_subscription'),
]
