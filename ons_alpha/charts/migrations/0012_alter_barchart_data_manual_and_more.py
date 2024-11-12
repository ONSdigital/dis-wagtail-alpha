# Generated by Django 4.2.16 on 2024-11-05 15:13

import wagtail.fields
import wagtailtables.blocks

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("charts", "0011_alter_barchart_x_tick_interval_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="barchart",
            name="data_manual",
            field=wagtail.fields.StreamField(
                [("table", 2)],
                blank=True,
                block_lookup={
                    0: ("wagtail.blocks.TextBlock", (), {"default": "[]", "label": "Data"}),
                    1: ("wagtail.blocks.ChoiceBlock", [], {"choices": wagtailtables.blocks.get_choices}),
                    2: ("wagtail.blocks.StructBlock", [[("table_data", 0), ("table_type", 1)]], {"label": "Table"}),
                },
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="linechart",
            name="data_manual",
            field=wagtail.fields.StreamField(
                [("table", 2)],
                blank=True,
                block_lookup={
                    0: ("wagtail.blocks.TextBlock", (), {"default": "[]", "label": "Data"}),
                    1: ("wagtail.blocks.ChoiceBlock", [], {"choices": wagtailtables.blocks.get_choices}),
                    2: ("wagtail.blocks.StructBlock", [[("table_data", 0), ("table_type", 1)]], {"label": "Table"}),
                },
                null=True,
            ),
        ),
    ]