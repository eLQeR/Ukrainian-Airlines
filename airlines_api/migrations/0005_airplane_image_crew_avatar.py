# Generated by Django 5.0.3 on 2024-04-07 21:40

import airlines_api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlines_api', '0004_alter_order_options_alter_ticket_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='airplane',
            name='image',
            field=models.ImageField(default='planes/no_plan_photo.png', upload_to=airlines_api.models.create_airplane_image_path),
        ),
        migrations.AddField(
            model_name='crew',
            name='avatar',
            field=models.ImageField(default='avatars/no_avatar.jpg', upload_to=airlines_api.models.create_avatar_path),
        ),
    ]
