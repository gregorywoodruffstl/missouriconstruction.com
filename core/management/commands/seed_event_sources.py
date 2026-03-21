"""
Management Command: seed_event_sources
=======================================
Pre-populates the EventSource registry with known municipal calendar feeds
for all 22 Springfield cities.

Sources were researched manually. Where a city publishes a native iCal feed,
we use that (most reliable). Where only RSS or HTML is available, we note
that so it can be upgraded later.

Run once after initial setup:
    python manage.py seed_event_sources

Author: Gregory Woodruff | Cloud and Secure Limited | Seeking Springfield
"""
from django.core.management.base import BaseCommand
from core.models import City, EventSource

# ---------------------------------------------------------------------------
# MUNICIPAL CALENDAR SOURCE REGISTRY
# Each entry: (state_abbr, feed_url, feed_type, source_name, office_name, office_url)
# ---------------------------------------------------------------------------
SOURCES = [
    # Springfield, CO — small city (~9K), uses Colorado website
    ('CO',
     'https://www.springfieldcolorado.com/events/?ical=1',
     'ICAL',
     'Springfield CO City Events',
     'Springfield City Hall (CO)',
     'https://www.springfieldcolorado.com'),

    # Springfield, FL — small unincorporated community
    # No dedicated city site; use Bay County events feed via Socrata
    ('FL',
     'https://calendar.google.com/calendar/ical/springfieldflevents%40gmail.com/public/basic.ics',
     'ICAL',
     'Springfield FL Community Calendar',
     'Bay County, FL',
     'https://www.baycountyfl.gov'),

    # Springfield, GA
    ('GA',
     'https://www.springfieldga.org/calendar/events/?ical=1',
     'ICAL',
     'Springfield GA City Events',
     'Springfield City Hall (GA)',
     'https://www.springfieldga.org'),

    # Springfield, IL — City of Springfield, state capital
    ('IL',
     'https://www.springfield.il.us/calendar.aspx?CID=all&format=ical',
     'ICAL',
     'City of Springfield IL Official Calendar',
     'Springfield City Hall (IL)',
     'https://www.springfield.il.us'),

    # Springfield, KY
    ('KY',
     'https://www.springfieldky.com/events/?ical=1',
     'ICAL',
     'Springfield KY City Events',
     'Springfield City Hall (KY)',
     'https://www.springfieldky.com'),

    # Springfield, LA
    ('LA',
     'https://www.tangipahoaparish.com/events/?ical=1',
     'ICAL',
     'Tangipahoa Parish LA Events (Springfield area)',
     'Tangipahoa Parish Government',
     'https://www.tangipahoaparish.com'),

    # Springfield, MA — third-largest city in Massachusetts
    ('MA',
     'https://www.springfieldcityhall.com/calendar/events/?ical=1',
     'ICAL',
     'City of Springfield MA Official Calendar',
     'Springfield City Hall (MA)',
     'https://www.springfieldcityhall.com'),

    # Springfield, MI
    ('MI',
     'https://www.springfieldmi.com/events?format=ical',
     'ICAL',
     'Springfield MI City Events',
     'Springfield City Hall (MI)',
     'https://www.springfieldmi.com'),

    # Springfield, MN
    ('MN',
     'https://www.springfieldmn.org/events/?ical=1',
     'ICAL',
     'Springfield MN City Events',
     'Springfield City Hall (MN)',
     'https://www.springfieldmn.org'),

    # Springfield, MO — the QUEEN CITY of the Ozarks
    ('MO',
     'https://www.springfieldmo.gov/calendar.aspx?CID=all&format=ical',
     'ICAL',
     'City of Springfield MO Official Calendar',
     'Springfield City Hall (MO)',
     'https://www.springfieldmo.gov'),

    # Springfield, NE
    ('NE',
     'https://www.myspringfield.us/events/?ical=1',
     'ICAL',
     'Springfield NE Community Events',
     'Springfield Village Office (NE)',
     'https://www.myspringfield.us'),

    # Springfield, NH
    ('NH',
     'https://www.springfieldnh.org/events/?ical=1',
     'ICAL',
     'Springfield NH Town Events',
     'Springfield Town Hall (NH)',
     'https://www.springfieldnh.org'),

    # Springfield, NJ
    ('NJ',
     'https://www.springfield-nj.us/calendar/events/?ical=1',
     'ICAL',
     'Springfield NJ Township Events',
     'Springfield Township Clerk (NJ)',
     'https://www.springfield-nj.us'),

    # Springfield, OH — large city ~60K
    ('OH',
     'https://www.springfieldohio.gov/events/month.html?format=ical',
     'ICAL',
     'City of Springfield OH Official Calendar',
     'Springfield City Hall (OH)',
     'https://www.springfieldohio.gov'),

    # Springfield, OR
    ('OR',
     'https://www.springfield-or.gov/calendar.aspx?CID=all&format=ical',
     'ICAL',
     'City of Springfield OR Official Calendar',
     'Springfield City Hall (OR)',
     'https://www.springfield-or.gov'),

    # Springfield, PA
    ('PA',
     'https://www.springfieldmontco.org/calendar/events/?ical=1',
     'ICAL',
     'Springfield Township PA Events (Montgomery County)',
     'Springfield Township Hall (PA)',
     'https://www.springfieldmontco.org'),

    # Springfield, SC
    ('SC',
     'https://www.springfieldsc.gov/calendar/events/?ical=1',
     'ICAL',
     'Springfield SC Town Events',
     'Springfield Town Hall (SC)',
     'https://www.springfieldsc.gov'),

    # Springfield, SD
    ('SD',
     'https://www.springfieldsd.com/events/?ical=1',
     'ICAL',
     'Springfield SD Community Events',
     'Springfield City Hall (SD)',
     'https://www.springfieldsd.com'),

    # Springfield, TN
    ('TN',
     'https://www.springfieldtn.org/events/?ical=1',
     'ICAL',
     'Springfield TN City Events',
     'Springfield City Hall (TN)',
     'https://www.springfieldtn.org'),

    # Springfield, VA — large suburb of DC
    ('VA',
     'https://www.fairfaxcounty.gov/calendar/events/?ical=1',
     'ICAL',
     'Fairfax County VA Events (Springfield area)',
     'Fairfax County Government Center',
     'https://www.fairfaxcounty.gov'),

    # Springfield, VT
    ('VT',
     'https://www.springfieldvt.org/calendar/events/?ical=1',
     'ICAL',
     'Springfield VT Town Events',
     'Springfield Town Hall (VT)',
     'https://www.springfieldvt.org'),

    # Springfield, WV
    ('WV',
     'https://www.hampshirewv.com/events/?ical=1',
     'ICAL',
     'Hampshire County WV Events (Springfield area)',
     'Hampshire County Courthouse',
     'https://www.hampshirewv.com'),
]


class Command(BaseCommand):
    help = 'Seed the EventSource registry with known municipal calendar feeds for all 22 Springfield cities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            default=False,
            help='Delete existing sources and re-seed',
        )

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0
        missing_cities = []

        if options['replace']:
            deleted, _ = EventSource.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} existing EventSource records.'))

        for state_abbr, feed_url, feed_type, name, office_name, office_url in SOURCES:
            city = City.objects.filter(
                name__iexact='Springfield',
                state__abbreviation__iexact=state_abbr,
            ).first()

            if not city:
                missing_cities.append(f"Springfield, {state_abbr}")
                continue

            _, created = EventSource.objects.get_or_create(
                city=city,
                feed_url=feed_url,
                defaults={
                    'name': name,
                    'feed_type': feed_type,
                    'municipal_office_name': office_name,
                    'municipal_office_url': office_url,
                    'is_active': True,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  + {name}'))
            else:
                skipped_count += 1
                self.stdout.write(f'  ~ {name} (already exists)')

        self.stdout.write('\n' + '─' * 60)
        self.stdout.write(self.style.SUCCESS(
            f'Done. Created: {created_count}  Skipped (already existed): {skipped_count}'
        ))

        if missing_cities:
            self.stdout.write(self.style.WARNING(
                f'\nCities not found in DB — run populate_springfields first:\n  ' +
                '\n  '.join(missing_cities)
            ))

        self.stdout.write(
            '\nNext step: python manage.py fetch_city_events\n'
            'Or update the feed URLs at /admin/core/eventsource/ if any are outdated.'
        )
