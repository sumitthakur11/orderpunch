# Generated by Django 5.1.1 on 2025-05-19 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tradingbot', '0013_watchlist_oi_watchlist_volume'),
    ]

    operations = [
        migrations.AddField(
            model_name='watchlist',
            name='instrument',
            field=models.CharField(blank=True, default=None, max_length=200, null=True),
        ),
    ]
