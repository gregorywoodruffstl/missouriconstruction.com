"""
setup_oauth.py — configure allauth SocialApp records for all three providers.

Run AFTER credentials are added to .env (or Azure App Settings).

Usage:
    python manage.py setup_oauth                  # Missouri Construction site
    python manage.py setup_oauth --site 2         # Seeking Springfield site (Site ID 2)
    python manage.py setup_oauth --all-sites      # Apply to all sites
    python manage.py setup_oauth --dry-run        # Preview without saving
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


PROVIDERS = [
    {
        'provider': 'google',
        'name': 'Google',
        'client_id_env': 'GOOGLE_CLIENT_ID',
        'secret_env': 'GOOGLE_CLIENT_SECRET',
        'key': '',
    },
    {
        'provider': 'facebook',
        'name': 'Facebook',
        'client_id_env': 'FACEBOOK_APP_ID',
        'secret_env': 'FACEBOOK_APP_SECRET',
        'key': '',
    },
    {
        'provider': 'apple',
        'name': 'Apple',
        'client_id_env': 'APPLE_CLIENT_ID',
        'secret_env': 'APPLE_KEY_ID',    # Key ID is stored as 'secret' in SocialApp
        'key': '',                        # Private key goes in settings.py SOCIALACCOUNT_PROVIDERS
    },
]


class Command(BaseCommand):
    help = 'Create/update allauth SocialApp records for Google, Facebook, and Apple'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site', type=int, default=1,
            help='Site ID to attach providers to (default: 1)'
        )
        parser.add_argument(
            '--all-sites', action='store_true',
            help='Attach providers to ALL sites in the database'
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Preview what would be created/updated without saving'
        )

    def handle(self, *args, **options):
        from allauth.socialaccount.models import SocialApp

        dry_run = options['dry_run']
        mode = 'DRY RUN' if dry_run else 'EXECUTE'

        self.stdout.write(self.style.MIGRATE_HEADING(f'\n=== Setup OAuth Providers [{mode}] ===\n'))

        # Determine which sites to attach to
        if options['all_sites']:
            sites = list(Site.objects.all())
        else:
            try:
                sites = [Site.objects.get(pk=options['site'])]
            except Site.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f'Site ID {options["site"]} not found. Run: python manage.py setup_oauth --all-sites'
                ))
                return

        self.stdout.write(f'Attaching providers to sites: {[s.domain for s in sites]}\n')

        for provider_data in PROVIDERS:
            provider = provider_data['provider']
            client_id = os.getenv(provider_data['client_id_env'], '')
            secret = os.getenv(provider_data['secret_env'], '')

            status = '✓ Credentials found' if (client_id and secret) else '⚠ No credentials yet (placeholder created)'
            self.stdout.write(f'  [{provider.upper()}] {status}')

            if not dry_run:
                app, created = SocialApp.objects.update_or_create(
                    provider=provider,
                    defaults={
                        'name': provider_data['name'],
                        'client_id': client_id,
                        'secret': secret,
                        'key': provider_data['key'],
                    }
                )
                verb = 'Created' if created else 'Updated'
                self.stdout.write(f'    {verb} SocialApp record (pk={app.pk})')

                # Attach to sites
                for site in sites:
                    if site not in app.sites.all():
                        app.sites.add(site)
                        self.stdout.write(f'    Linked to site: {site.domain}')
                    else:
                        self.stdout.write(f'    Already linked to: {site.domain}')

        self.stdout.write('')

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run complete — nothing saved. Remove --dry-run to apply.'))
        else:
            self.stdout.write(self.style.SUCCESS('OAuth providers configured.\n'))
            self.stdout.write('Next steps:')
            self.stdout.write('  1. Add credentials to .env (or Azure App Settings)')
            self.stdout.write('  2. Re-run this command to update with real credentials')
            self.stdout.write('  3. Test login URLs:')
            self.stdout.write('       /accounts/google/login/')
            self.stdout.write('       /accounts/facebook/login/')
            self.stdout.write('       /accounts/apple/login/')
            self.stdout.write('')
            self.stdout.write('Required redirect URIs to register with each provider:')
            self.stdout.write('  Google:   https://missouriconstruction.com/accounts/google/login/callback/')
            self.stdout.write('  Facebook: https://missouriconstruction.com/accounts/facebook/login/callback/')
            self.stdout.write('  Apple:    https://missouriconstruction.com/accounts/apple/login/callback/')
            self.stdout.write('  (Also add localhost:8002 versions for local testing)')
