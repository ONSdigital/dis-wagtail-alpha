# Generated by Django 4.2.14 on 2024-07-18 13:06

import django.db.models.deletion
import wagtail.search.index

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("topics", "0003_alter_topicpage_topic_alter_topicsectionpage_topic"),
        ("release_calendar", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Bundle",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("collection_reference", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("publication_date", models.DateTimeField(blank=True, null=True)),
                ("status", models.CharField(default="PENDING", max_length=32)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bundles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "release_calendar_page",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bundles",
                        to="release_calendar.releasepage",
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bundles",
                        to="topics.topicpage",
                    ),
                ),
            ],
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
    ]
