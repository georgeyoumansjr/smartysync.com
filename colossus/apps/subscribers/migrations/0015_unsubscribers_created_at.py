# Generated by Django 2.2 on 2024-03-25 15:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('subscribers', '0014_auto_20240307_1053'),
    ]

    operations = [
        migrations.AddField(
            model_name='unsubscribers',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at'),
        ),
    ]
