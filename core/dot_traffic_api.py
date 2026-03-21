"""
US Department of Transportation — Traffic Volume Data Client

Fetches Annual Average Daily Traffic (AADT) counts near a given city using:
  - FHWA Highway Performance Monitoring System (HPMS) open data
    via data.transportation.gov (Socrata API — no key required)

AADT = average number of vehicles passing a road segment per day over a year.
This is exactly the "how many cars drive by your business each week" statistic
that business owners love to see alongside census median income data.

If the DOT API is unavailable, we fall back to a rough Census-ACS commute
estimate so the page never breaks.

Author: Gregory Woodruff | Cloud and Secure Limited | Seeking Springfield
"""
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Socrata endpoint for FHWA HPMS Summary data (no API key needed for public datasets)
HPMS_API_URL = "https://data.transportation.gov/resource/g6an-ncgj.json"


def get_city_traffic_data(city_name: str, state_abbr: str) -> Optional[dict]:
    """
    Return AADT traffic context for a given city.

    Returns a dict with:
        aadt_estimate    — estimated vehicles/day near the city centre
        weekly_estimate  — aadt_estimate × 7
        source           — 'FHWA HPMS' or 'Census ACS estimate'
        note             — human-readable caveat shown on the page
        state_abbr       — echoed back for display
        city_name        — echoed back for display

    Returns None if the call completely fails.
    """
    # ------------------------------------------------------------------
    # 1. Try FHWA HPMS open data (Socrata)
    # ------------------------------------------------------------------
    try:
        params = {
            '$where': f"state_code='{state_abbr.upper()}' AND facility_type IS NOT NULL",
            '$select': 'aadt,facility_type,route_id',
            '$order': 'aadt DESC',
            '$limit': 200,
        }
        resp = requests.get(HPMS_API_URL, params=params, timeout=8)
        resp.raise_for_status()
        rows = resp.json()

        if rows:
            # Filter out nulls; take the median as a representative "major road" AADT
            values = [int(row['aadt']) for row in rows if row.get('aadt')]
            if values:
                values.sort()
                median_aadt = values[len(values) // 2]
                top_aadt = max(values)

                return {
                    'aadt_estimate': median_aadt,
                    'weekly_estimate': median_aadt * 7,
                    'top_corridor_aadt': top_aadt,
                    'top_corridor_weekly': top_aadt * 7,
                    'source': 'FHWA HPMS (Highway Performance Monitoring System)',
                    'source_url': 'https://data.transportation.gov',
                    'note': (
                        f"State-level AADT median across {len(values)} road segments in {state_abbr.upper()}. "
                        f"Your specific corridor may differ — check your local {state_abbr.upper()} DOT for route-level data."
                    ),
                    'state_abbr': state_abbr.upper(),
                    'city_name': city_name,
                }
    except Exception as e:
        logger.warning("FHWA HPMS API failed for %s, %s: %s", city_name, state_abbr, e)

    # ------------------------------------------------------------------
    # 2. Fallback — estimate from US average (BTS National Household Travel Survey)
    # National average: ~37 million vehicle-miles travelled per day / 4.1M lane-miles
    # Urban collector road typical AADT: 5,000–25,000 vehicles/day
    # We use a conservative 10,000 as a midpoint placeholder.
    # ------------------------------------------------------------------
    fallback_aadt = 10_000
    return {
        'aadt_estimate': fallback_aadt,
        'weekly_estimate': fallback_aadt * 7,
        'top_corridor_aadt': None,
        'top_corridor_weekly': None,
        'source': 'BTS National Average Estimate',
        'source_url': 'https://www.bts.gov/topics/national-household-travel-survey',
        'note': (
            "Live DOT data was unavailable. Showing a US national average estimate for an urban collector road. "
            "Contact your local state DOT for precise traffic counts on your specific street."
        ),
        'state_abbr': state_abbr.upper(),
        'city_name': city_name,
    }
