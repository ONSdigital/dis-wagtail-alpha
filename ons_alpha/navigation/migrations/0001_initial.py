# Generated by Django 4.2.11 on 2024-06-21 11:03

import django.db.models.deletion

from django.db import migrations, models

import ons_alpha.utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("wagtailcore", "0040_page_draft_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="NavigationSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False
                    ),
                ),
                (
                    "primary_navigation",
                    ons_alpha.utils.fields.StreamField(blank=True, use_json_field=True),
                ),
                (
                    "secondary_navigation",
                    ons_alpha.utils.fields.StreamField(blank=True, use_json_field=True),
                ),
                (
                    "footer_navigation",
                    ons_alpha.utils.fields.StreamField(blank=True, use_json_field=True),
                ),
                (
                    "footer_links",
                    ons_alpha.utils.fields.StreamField(blank=True, use_json_field=True),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.site",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
