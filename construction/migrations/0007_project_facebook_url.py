from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('construction', '0006_powerbi_reports'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='facebook_post_url',
            field=models.URLField(blank=True, help_text='Facebook post URL — paste here after publishing to the Cardinals group'),
        ),
    ]
