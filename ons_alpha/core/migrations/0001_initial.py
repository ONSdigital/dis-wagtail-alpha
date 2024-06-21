import django.db.models.deletion
from django.db import migrations, models

import modelcluster.fields
import wagtail.fields

import ons_alpha.utils.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("images", "0001_initial"),
        ("wagtailcore", "0032_add_bulk_delete_page_permission"),
    ]

    operations = [
        migrations.CreateModel(
            name="CallToActionSnippet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "link",
                    ons_alpha.utils.fields.StreamField(use_json_field=True),
                ),
                (
                    "summary",
                    wagtail.fields.RichTextField(blank=True, max_length=255),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.CustomImage",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="SocialMediaSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "twitter_handle",
                    models.CharField(
                        blank=True,
                        help_text="Your Twitter username without the @, e.g. katyperry",
                        max_length=255,
                    ),
                ),
                (
                    "facebook_app_id",
                    models.CharField(
                        blank=True, help_text="Your Facebook app ID.", max_length=255
                    ),
                ),
                (
                    "default_sharing_text",
                    models.CharField(
                        blank=True,
                        help_text="Default sharing text to use if social text has not been set on a page.",
                        max_length=255,
                    ),
                ),
                (
                    "site_name",
                    models.CharField(
                        blank=True,
                        default="ONS Alpha",
                        help_text="Site name, used by Open Graph.",
                        max_length=255,
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.Site",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="SystemMessagesSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title_404",
                    models.CharField(
                        default="Page not found", max_length=255, verbose_name="Title"
                    ),
                ),
                (
                    "body_404",
                    wagtail.fields.RichTextField(
                        default="<p>You may be trying to find a page that doesn&rsquo;t exist or has been moved.</p>",
                        verbose_name="Text",
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.Site",
                    ),
                ),
            ],
            options={"abstract": False, "verbose_name": "system messages"},
        ),
        migrations.CreateModel(
            name="Tracking",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "google_tag_manager_id",
                    models.CharField(
                        blank="True",
                        help_text="Your Google Tag Manager ID",
                        max_length=255,
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.Site",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="PageRelatedPage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "page",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="wagtailcore.Page",
                    ),
                ),
                (
                    "parent",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="page_related_pages",
                        to="wagtailcore.Page",
                    ),
                ),
            ],
            options={"ordering": ["sort_order"], "abstract": False},
        ),
    ]
