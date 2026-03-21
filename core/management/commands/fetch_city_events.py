"""
Management Command: fetch_city_events
=====================================
Pulls civic events from all active EventSource records and writes them
to the Event model.

Usage:
    python manage.py fetch_city_events              # all active sources
    python manage.py fetch_city_events --city IL    # only Illinois Springfields
    python manage.py fetch_city_events --source 5   # a single EventSource by ID
    python manage.py fetch_city_events --dry-run    # parse but don't save

Schedule (Azure / cron):
    Run daily at 6 AM — municipal calendars don't change faster than that.

Author: Gregory Woodruff | Cloud and Secure Limited | Seeking Springfield
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import EventSource, Site


class Command(BaseCommand):
    help = 'Fetch civic calendar events from all municipal sources for every Springfield city'

    def add_arguments(self, parser):
        parser.add_argument(
            '--city',
            type=str,
            default=None,
            help='Filter by state abbreviation (e.g. IL)',
        )
        parser.add_argument(
            '--source',
            type=int,
            default=None,
            help='Fetch only a single EventSource by ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Parse feeds but do not write to the database',
        )

    def handle(self, *args, **options):
        from core.calendar_scraper import scrape_source

        site = Site.objects.filter(is_active=True).first()

        sources = EventSource.objects.filter(is_active=True).select_related('city', 'city__state')

        if options['source']:
            sources = sources.filter(id=options['source'])
        elif options['city']:
            sources = sources.filter(city__state__abbreviation__iexact=options['city'])

        total_sources = sources.count()
        if total_sources == 0:
            self.stdout.write(self.style.WARNING('No active EventSource records found.'))
            self.stdout.write(
                'Run: python manage.py seed_event_sources  to populate the municipal calendar registry.'
            )
            return

        self.stdout.write(f'Fetching events from {total_sources} sources...\n')

        total = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}

        for source in sources:
            label = f"{source.city.name}, {source.city.state.abbreviation} — {source.name}"
            self.stdout.write(f'  Scraping {label}... ', ending='')

            if options['dry_run']:
                self.stdout.write(self.style.WARNING('[DRY RUN — skipped]'))
                continue

            result = scrape_source(source, site=site)

            created  = result['created']
            updated  = result['updated']
            skipped  = result['skipped']
            errors   = result['errors']

            total['created'] += created
            total['updated'] += updated
            total['skipped'] += skipped
            total['errors']  += len(errors)

            status = f"✓ +{created} new, {updated} updated, {skipped} skipped"
            if errors:
                status += f"  ⚠ {errors[0][:80]}"
                self.stdout.write(self.style.ERROR(status))
            else:
                self.stdout.write(self.style.SUCCESS(status))

        self.stdout.write('\n' + '─' * 60)
        self.stdout.write(self.style.SUCCESS(
            f"Done. Created: {total['created']}  Updated: {total['updated']}  "
            f"Skipped: {total['skipped']}  Errors: {total['errors']}"
        ))
