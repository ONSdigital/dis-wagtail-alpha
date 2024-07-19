# Generated by Django 4.2.14 on 2024-07-19 14:55

from django.db import migrations
import ons_alpha.core.blocks.markup
import ons_alpha.core.blocks.related
import ons_alpha.core.blocks.snippets
import wagtail.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtailmath.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("bulletins", "0004_bulletintopicrelationship"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bulletinpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", ons_alpha.core.blocks.markup.HeadingBlock(show_back_to_toc=False)),
                    ("rich_text", wagtail.blocks.RichTextBlock()),
                    (
                        "panel",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "variant",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("announcement", "Announcement"),
                                            ("bare", "Bare"),
                                            ("branded", "Branded"),
                                            ("error", "Error"),
                                            ("ghost", "Ghost"),
                                            ("success", "Success"),
                                            ("warn-branded", "Warn (branded)"),
                                            ("warn", "Warn"),
                                        ]
                                    ),
                                ),
                                ("title", wagtail.blocks.CharBlock(required=False)),
                                (
                                    "body",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "italic", "link", "ol", "ul", "document-link"]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ("table", ons_alpha.core.blocks.markup.TableBlock(group="DataVis")),
                    ("equation", wagtailmath.blocks.MathBlock(group="DataVis", icon="decimal")),
                    (
                        "ons_embed",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "url",
                                    wagtail.blocks.URLBlock(
                                        help_text="Must start with <code>https://www.ons.gov.uk/visualisations/</code> to your URL."
                                    ),
                                ),
                                ("title", wagtail.blocks.CharBlock(default="Interactive chart")),
                            ],
                            group="DataVis",
                        ),
                    ),
                    ("embed", wagtail.embeds.blocks.EmbedBlock()),
                    ("image", wagtail.images.blocks.ImageChooserBlock()),
                    (
                        "related_links",
                        ons_alpha.core.blocks.related.RelatedLinksBlock(
                            wagtail.blocks.StructBlock(
                                [
                                    ("page", wagtail.blocks.PageChooserBlock(required=False)),
                                    ("external_url", wagtail.blocks.URLBlock(label="or External Link", required=False)),
                                    (
                                        "title",
                                        wagtail.blocks.CharBlock(
                                            help_text="Populate when adding an external link. When choosing a page, you can leave it blank to use the page's own title",
                                            required=False,
                                        ),
                                    ),
                                    ("description", wagtail.blocks.CharBlock(required=False)),
                                ]
                            )
                        ),
                    ),
                    ("chart", ons_alpha.core.blocks.snippets.ChartChooserBlock(group="DataVis")),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="bulletinpage",
            name="updates",
            field=wagtail.fields.StreamField(
                [
                    (
                        "corrections",
                        wagtail.blocks.ListBlock(
                            wagtail.blocks.StructBlock(
                                [
                                    ("when", wagtail.blocks.DateTimeBlock()),
                                    (
                                        "text",
                                        wagtail.blocks.RichTextBlock(
                                            features=["bold", "italic", "link", "ol", "ul", "document-link"]
                                        ),
                                    ),
                                ]
                            ),
                            template="templates/components/streamfield/corrections_block.html",
                        ),
                    ),
                    (
                        "notices",
                        wagtail.blocks.ListBlock(
                            wagtail.blocks.StructBlock(
                                [
                                    ("when", wagtail.blocks.DateTimeBlock()),
                                    (
                                        "text",
                                        wagtail.blocks.RichTextBlock(
                                            features=["bold", "italic", "link", "ol", "ul", "document-link"]
                                        ),
                                    ),
                                ]
                            ),
                            template="templates/components/streamfield/notices_block.html",
                        ),
                    ),
                ],
                blank=True,
            ),
        ),
    ]