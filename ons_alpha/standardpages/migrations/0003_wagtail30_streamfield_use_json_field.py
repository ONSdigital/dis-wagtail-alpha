# Generated by Django 3.2.12 on 2022-05-31 10:42

from django.db import migrations

import ons_alpha.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("standardpages", "0002_remove_informationpagerelatedpage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informationpage",
            name="body",
            field=ons_alpha.utils.fields.StreamField(use_json_field=True),
        ),
    ]
