# Generated by Django 4.2.11 on 2024-06-21 10:59

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "__first__"),
        ("wagtailcore", "0040_page_draft_title"),
        ("images", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("listing_title", models.CharField(blank=True, max_length=255)),
                ("listing_summary", models.CharField(blank=True, max_length=255)),
                ("social_text", models.CharField(blank=True, max_length=255)),
                ("strapline", models.CharField(blank=True, max_length=255)),
                (
                    "call_to_action",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="core.calltoactionsnippet",
                    ),
                ),
                (
                    "listing_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page", models.Model),
        ),
    ]
