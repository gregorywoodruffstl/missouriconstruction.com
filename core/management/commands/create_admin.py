"""
Create or reset the Django admin (superuser) account.

Reads credentials from environment variables — never hardcoded.

Usage in Azure Kudu SSH console:
    cd /home/site/wwwroot
    source /antenv/bin/activate
    ADMIN_USERNAME=woody ADMIN_EMAIL=gregory.woodruff@cloudandsecurelimited.com \
    ADMIN_PASSWORD=YourSecurePassword123 python manage.py create_admin

Or set them in Azure App Settings and run:
    python manage.py create_admin
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or reset the Django superuser account from environment variables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default=None,
            help='Username (overrides ADMIN_USERNAME env var)'
        )
        parser.add_argument(
            '--email',
            default=None,
            help='Email (overrides ADMIN_EMAIL env var)'
        )
        parser.add_argument(
            '--password',
            default=None,
            help='Password (overrides ADMIN_PASSWORD env var)'
        )

    def handle(self, *args, **options):
        username = options['username'] or os.environ.get('ADMIN_USERNAME', 'woody')
        email = options['email'] or os.environ.get('ADMIN_EMAIL', '')
        password = options['password'] or os.environ.get('ADMIN_PASSWORD', '')

        if not password:
            self.stderr.write(self.style.ERROR(
                'No password supplied. Set ADMIN_PASSWORD env var or use --password.'
            ))
            return

        if not email:
            self.stderr.write(self.style.WARNING(
                'No email supplied. Set ADMIN_EMAIL env var or use --email.'
            ))

        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Superuser "{username}" created successfully.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Superuser "{username}" already existed — password and flags updated.'
            ))

        self.stdout.write(f'  Email:       {email or "(not set)"}')
        self.stdout.write(f'  is_staff:    True')
        self.stdout.write(f'  is_superuser: True')
        self.stdout.write('')
        self.stdout.write('You can now log in at: /admin/')
