# Generated by Django 4.2.14 on 2024-07-29 17:10

import wagtail.blocks
import wagtail.fields

from django.db import migrations

import ons_alpha.datasets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ("bundles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="bundle",
            name="datasets",
            field=wagtail.fields.StreamField(
                [
                    (
                        "dataset_lookup",
                        ons_alpha.datasets.blocks.DatasetChooserBlock(
                            label="Lookup Dataset", template="templates/components/streamfield/dataset_link_block.html"
                        ),
                    ),
                    (
                        "manual_link",
                        wagtail.blocks.StructBlock(
                            [
                                ("title", wagtail.blocks.CharBlock(required=True)),
                                ("description", wagtail.blocks.TextBlock(required=False)),
                                ("url", wagtail.blocks.URLBlock(required=True)),
                            ],
                            label="Manually Linked Dataset",
                            required=False,
                        ),
                    ),
                ],
                blank=True,
            ),
        ),
        migrations.DeleteModel(
            name="BundleLink",
        ),
    ]
