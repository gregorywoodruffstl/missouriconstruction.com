import os


def google_analytics(request):
    """Inject GA4 Measurement ID into every template context."""
    return {
        'ga_measurement_id': os.getenv('GA_MEASUREMENT_ID', ''),
    }
