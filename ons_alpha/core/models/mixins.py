from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


__all__ = [
    "ListingFieldsMixin",
    "SocialFieldsMixin",
]


class ListingFieldsMixin(models.Model):
    """
    Generic listing fields abstract class to add listing image/text to any new content type easily.
    """

    listing_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Choose the image you wish to be displayed when this page appears in listings",
    )
    listing_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Override the page title used when this page appears in listings",
    )
    listing_summary = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "The text summary used when this page appears in listings. It's also used as the "
            "description for search engines if the 'Meta description' field above is not defined.",
        ),
    )

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            heading="Listing information",
            children=[
                FieldPanel("listing_image"),
                FieldPanel("listing_title"),
                FieldPanel("listing_summary"),
            ],
        )
    ]


class SocialFieldsMixin(models.Model):
    """
    Generic social fields abstract class to add social image/text to any new content type easily.
    """

    social_image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    social_text = models.CharField(max_length=255, blank=True)

    class Meta:
        abstract = True

    promote_panels = [
        MultiFieldPanel(
            heading="Social networks",
            children=[
                FieldPanel("social_image"),
                FieldPanel("social_text"),
            ],
        )
    ]
