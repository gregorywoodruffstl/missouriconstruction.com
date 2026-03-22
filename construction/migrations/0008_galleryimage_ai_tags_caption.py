from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('construction', '0007_project_facebook_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryimage',
            name='ai_tags',
            field=models.JSONField(blank=True, default=list, help_text='Auto-generated tags from Azure AI Vision'),
        ),
        migrations.AddField(
            model_name='galleryimage',
            name='ai_caption',
            field=models.TextField(blank=True, help_text='Auto-generated description from Azure AI Vision'),
        ),
    ]
