# Generated by Django 5.1.1 on 2025-05-20 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Tradingbot', '0015_rename_order_type_orderobject_ordertype_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='broker',
            name='funds',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
