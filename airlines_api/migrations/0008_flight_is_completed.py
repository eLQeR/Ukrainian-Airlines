# Generated by Django 5.0.3 on 2024-04-20 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines_api', '0007_remove_airplane_speed_per_hour'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
