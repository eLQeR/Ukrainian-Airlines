# Generated by Django 5.0.3 on 2024-04-03 17:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='passenger',
            field=models.OneToOneField(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='ticket', to='airlines_api.passenger'),
            preserve_default=False,
        ),
    ]