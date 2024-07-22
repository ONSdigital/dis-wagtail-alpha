# Generated by Django 4.2.14 on 2024-07-22 09:31

import wagtail.blocks
import wagtail.fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bulletins", "0005_alter_bulletinpage_body_alter_bulletinpage_updates"),
    ]

    operations = [
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
