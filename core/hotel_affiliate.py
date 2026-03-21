"""
Hotel Affiliate Links — Seeking Springfield
============================================
Generates affiliate deep-links to major OTA and hotel-chain booking pages
for any Springfield city.  No API key is required to generate links — you
earn commissions once you've enrolled in each program.

HOW THE EXPEDIA TRAVEL CREATOR LINKS WORK
------------------------------------------
Expedia's Travel Creator program generates shortlinks in this format:
    https://expedia.com/affiliates/[page-slug].[TRACKING_CODE]

Your tracking code is the part AFTER the dot — e.g. "Md9OTSL".
It stays the same across all 22 links you generate.

SETUP INSTRUCTIONS
------------------
1.  In the Expedia Travel Creator tool, search for hotels in each city,
    e.g. "Hotels in Springfield, IL" → click Create Link.
2.  Paste each generated URL into EXPEDIA_CITY_LINKS below, keyed by
    state abbreviation (lowercase).
3.  For a quick fallback, set your tracking code in .env:
        AFFILIATE_EXPEDIA_TRACKING=Md9OTSL
    Any city without a custom link will use a generic search URL + that code.

Booking.com affiliate sign-up → https://www.booking.com/affiliate-program.html

WHICH HOTEL CHAINS ARE IN ALL 22 SPRINGFIELDS?
-----------------------------------------------
  Tier 1 – Definitively in all 22:
    Marriott family (Courtyard, Fairfield, Residence Inn)
    Hilton family (Hampton Inn, Holiday Inn Express)
    Choice Hotels (Comfort Inn, Sleep Inn, Quality Inn)
    Best Western (Best Western, BW Plus, SureStay)
    Wyndham (Super 8, Days Inn, La Quinta)

  Tier 2 – Present in most (16+) Springfields:
    IHG (Holiday Inn, Staybridge, Candlewood)
    Hyatt (Hyatt Place)

Author: Gregory Woodruff | Cloud and Secure Limited | Seeking Springfield
"""

from urllib.parse import quote_plus
from django.conf import settings


# ---------------------------------------------------------------------------
# Pull affiliate settings
# ---------------------------------------------------------------------------
def _aff(attr: str, default: str = "") -> str:
    return getattr(settings, attr, default)


# ---------------------------------------------------------------------------
# PASTE YOUR 22 EXPEDIA TRAVEL CREATOR LINKS HERE
# Key = state abbreviation (lowercase), Value = full URL from creator tool
#
# Example after generating in the Creator tool:
#   "il": "https://expedia.com/affiliates/hotel-search-springfield-il.Md9OTSL",
#   "mo": "https://expedia.com/affiliates/hotel-search-springfield-mo.Md9OTSL",
# ---------------------------------------------------------------------------
EXPEDIA_CITY_LINKS: dict[str, str] = {
    "il": "https://expedia.com/affiliates/hotel-search-springfield.vMuLnPe",
    "mo": "https://expedia.com/affiliates/hotel-search-springfield.yKCsWwG",
    "co": "https://expedia.com/affiliates/hotel-search-springfield.2sdx5LV",
    "fl": "https://expedia.com/affiliates/hotel-search-springfield.i55Of2m",
    "ga": "https://expedia.com/affiliates/hotel-search-springfield.3RJLq5K",
    "ky": "https://expedia.com/affiliates/hotel-search-springfield.v1mfSnA",
    "la": "https://expedia.com/affiliates/hotel-search-springfield.wR520IH",
    "ma": "https://expedia.com/affiliates/hotel-search-springfield.JKS76Sj",
    "mi": "https://expedia.com/affiliates/hotel-search-springfield.aRSnh2j",
    "mn": "https://expedia.com/affiliates/hotel-search-springfield.l8UZbwJ",
    "ne": "https://expedia.com/affiliates/hotel-search-springfield.sFnsVDB",
    "nh": "https://expedia.com/affiliates/hotel-search-springfield.rt4pbCF",
    "nj": "https://expedia.com/affiliates/hotel-search-springfield.syTmR9n",
    "oh": "https://expedia.com/affiliates/hotel-search-springfield.lyx7d20",
    "or": "https://expedia.com/affiliates/hotel-search-springfield.bs1Hwpg",
    "pa": "https://expedia.com/affiliates/hotel-search-springfield.5MhNFxo",
    "sc": "https://expedia.com/affiliates/hotel-search-springfield.Wubvrvk",
    "sd": "https://expedia.com/affiliates/hotel-search-springfield.t1lASHa",
    "tn": "https://expedia.com/affiliates/hotel-search-springfield.HrfArUI",
    "va": "https://expedia.com/affiliates/hotel-search-springfield.VTcBuco",
    "vt": "https://expedia.com/affiliates/hotel-search-springfield.LTas6wS",
    "wv": "https://expedia.com/affiliates/hotel-search-springfield.M82Gq25",
}

# Same format for Hotels.com (same Creator tool, different brand links)
HOTELS_COM_CITY_LINKS: dict[str, str] = {
    # "il": "https://expedia.com/affiliates/hotels-com-springfield-il.Md9OTSL",
}


# ---------------------------------------------------------------------------
# OTA deep-link builders
# ---------------------------------------------------------------------------

def _expedia_link(city_name: str, state_abbr: str) -> dict:
    state_key = state_abbr.lower()
    # Use the pre-generated Travel Creator shortlink if available
    if state_key in EXPEDIA_CITY_LINKS:
        url = EXPEDIA_CITY_LINKS[state_key]
    else:
        # Fallback: build a search URL with the tracking code appended
        dest = quote_plus(f"Springfield, {state_abbr}")
        tracking = _aff("AFFILIATE_EXPEDIA_TRACKING")  # e.g. "Md9OTSL"
        url = f"https://www.expedia.com/Hotel-Search?destination={dest}"
        if tracking:
            url += f"&affcid={tracking}"
    return {
        "name": "Expedia",
        "logo": "expedia",
        "url": url,
        "tagline": "Compare all hotels & save",
        "tier": "ota",
        "commission": "4–6 %",
        "cta": "Search Hotels on Expedia",
    }


def _hotels_com_link(city_name: str, state_abbr: str) -> dict:
    state_key = state_abbr.lower()
    if state_key in HOTELS_COM_CITY_LINKS:
        url = HOTELS_COM_CITY_LINKS[state_key]
    else:
        dest = quote_plus(f"Springfield, {state_abbr}")
        tracking = _aff("AFFILIATE_EXPEDIA_TRACKING")  # same tracking code works for Hotels.com
        url = f"https://www.hotels.com/search.do?q-destination={dest}&resolved-location=CITY"
        if tracking:
            url += f"&pos={tracking}"
    return {
        "name": "Hotels.com",
        "logo": "hotels_com",
        "url": url,
        "tagline": "Collect a free night for every 10 booked",
        "tier": "ota",
        "commission": "4–6 %",
        "cta": "Find Hotels.com Deals",
    }


def _booking_com_link(city_name: str, state_abbr: str) -> dict:
    dest = quote_plus(f"Springfield, {state_abbr}, United States")
    aid = _aff("AFFILIATE_BOOKING_COM_AID")
    url = f"https://www.booking.com/searchresults.html?ss={dest}"
    if aid:
        url += f"&aid={aid}"
    return {
        "name": "Booking.com",
        "logo": "booking_com",
        "url": url,
        "tagline": "Genius loyalty discounts included",
        "tier": "ota",
        "commission": "3–6 %",
        "cta": "Browse Booking.com",
    }


# ---------------------------------------------------------------------------
# Chain direct-booking deep-links
# ---------------------------------------------------------------------------
CHAIN_TEMPLATES = [
    {
        "name": "Hampton Inn (Hilton)",
        "logo": "hilton",
        "url_template": "https://www.hilton.com/en/hotels/?q={dest}&brand%5B%5D=HP",
        "tagline": "Hilton Honors points on every stay",
        "tier": "chain",
        "commission": "Hilton partner program",
        "cta": "Book Hampton Inn",
    },
    {
        "name": "Courtyard by Marriott",
        "logo": "marriott",
        "url_template": "https://www.marriott.com/search/default.mi?q={dest}&propertyBrand=CY",
        "tagline": "Marriott Bonvoy points on every stay",
        "tier": "chain",
        "commission": "Marriott partner program",
        "cta": "Book Courtyard by Marriott",
    },
    {
        "name": "Holiday Inn / IHG",
        "logo": "ihg",
        "url_template": "https://www.ihg.com/holidayinn/hotels/us/en/find-hotels/hotel/results?qDest={dest}&brand=HI",
        "tagline": "IHG One Rewards on every stay",
        "tier": "chain",
        "commission": "IHG affiliate program",
        "cta": "Book Holiday Inn",
    },
    {
        "name": "Best Western",
        "logo": "bestwestern",
        "url_template": "https://www.bestwestern.com/en_US/find-a-hotel.html?hotel_name={dest}",
        "tagline": "Best Western Rewards on stay",
        "tier": "chain",
        "commission": "Best Western affiliate program",
        "cta": "Book Best Western",
    },
    {
        "name": "La Quinta (Wyndham)",
        "logo": "wyndham",
        "url_template": "https://www.wyndhamhotels.com/laquinta/hotels?q={dest}",
        "tagline": "Wyndham Rewards — free nights fast",
        "tier": "chain",
        "commission": "Wyndham affiliate program",
        "cta": "Book La Quinta",
    },
    {
        "name": "Comfort Inn (Choice Hotels)",
        "logo": "choice",
        "url_template": "https://www.choicehotels.com/hotels?destination={dest}&brand=CI",
        "tagline": "Choice Privileges rewards from day 1",
        "tier": "chain",
        "commission": "Choice Hotels affiliate program",
        "cta": "Book Comfort Inn",
    },
]


def _chain_links(city_name: str, state_abbr: str) -> list[dict]:
    dest = quote_plus(f"Springfield {state_abbr}")
    links = []
    for chain in CHAIN_TEMPLATES:
        link = dict(chain)  # shallow copy
        link["url"] = chain["url_template"].format(dest=dest)
        del link["url_template"]
        links.append(link)
    return links


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_hotel_links(city) -> dict:
    """
    Return hotel affiliate links for a city page.

    Returns:
        {
            "ota": [list of OTA dicts],
            "chains": [list of chain dicts],
            "affiliate_active": bool,  # True if at least one ID is set
            "sign_up_url": str,        # fallback if no IDs yet
        }
    """
    city_name = city.name
    state_abbr = city.state.abbreviation if city.state else ""

    ota_links = [
        _expedia_link(city_name, state_abbr),
        _hotels_com_link(city_name, state_abbr),
        _booking_com_link(city_name, state_abbr),
    ]
    chain_links = _chain_links(city_name, state_abbr)

    # Check if tracking is active — either a city shortlink exists or tracking code is set
    state_key = state_abbr.lower() if state_abbr else ""
    affiliate_active = bool(
        state_key in EXPEDIA_CITY_LINKS
        or _aff("AFFILIATE_EXPEDIA_TRACKING")
        or _aff("AFFILIATE_BOOKING_COM_AID")
    )

    return {
        "ota": ota_links,
        "chains": chain_links,
        "affiliate_active": affiliate_active,
        "sign_up_url": "https://join.expediagroup.com/en/",
    }
