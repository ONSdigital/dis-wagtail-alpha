# Generated by Django 4.2.14 on 2024-07-31 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("topics", "0004_topicpage_summary_topicsectionpage_summary"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topicpage",
            name="summary",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="topicsectionpage",
            name="summary",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
