# Generated by Django 4.2.11 on 2024-07-01 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulletins', '0004_bulletinpage_next_release_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulletinpage',
            name='summary',
            field=models.TextField(default='Summary'),
            preserve_default=False,
        ),
    ]
