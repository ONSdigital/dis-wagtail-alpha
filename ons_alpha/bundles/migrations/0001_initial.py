# Generated by Django 4.2.14 on 2024-07-25 09:43

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
import wagtail.search.index

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("wagtailcore", "0093_uploadedfile"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("topics", "0003_alter_topicpage_topic_alter_topicsectionpage_topic"),
        ("release_calendar", "0001_initial"),
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
            options={
                "abstract": False,
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name="BundlePage",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "page",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="wagtailcore.page"
                    ),
                ),
                (
                    "parent",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="bundled_pages", to="bundles.bundle"
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="BundleLink",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("url", models.URLField(blank=True)),
                ("title", models.CharField(blank=True, max_length=255)),
                ("description", wagtail.fields.RichTextField(blank=True)),
                (
                    "parent",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="bundled_links", to="bundles.bundle"
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
