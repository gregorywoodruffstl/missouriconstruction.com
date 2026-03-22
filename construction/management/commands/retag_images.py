from django.core.management.base import BaseCommand
from construction.models import GalleryImage


class Command(BaseCommand):
    help = 'Re-run Azure AI Vision tagging on gallery images that have no tags or caption'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Retag ALL images, even those already tagged',
        )
        parser.add_argument(
            '--id',
            type=int,
            help='Retag a single image by ID',
        )

    def handle(self, *args, **options):
        if options.get('id'):
            qs = GalleryImage.objects.filter(pk=options['id'])
        elif options.get('all'):
            qs = GalleryImage.objects.all()
        else:
            # Default: only images missing tags or caption
            qs = GalleryImage.objects.filter(ai_tags=[], ai_caption='')

        total = qs.count()
        self.stdout.write(f'Tagging {total} image(s)...')

        for img in qs:
            self.stdout.write(f'  ID:{img.pk} {img.image.name}', ending=' ')
            img._run_ai_tagging()
            img.refresh_from_db()
            if img.ai_caption:
                self.stdout.write(self.style.SUCCESS(f'OK: "{img.ai_caption}"'))
                if img.ai_tags:
                    self.stdout.write(f'    Tags: {", ".join(img.ai_tags)}')
            else:
                self.stdout.write(self.style.WARNING('WARNING: No caption returned'))

        self.stdout.write(self.style.SUCCESS(f'Done -- {total} image(s) processed.'))
