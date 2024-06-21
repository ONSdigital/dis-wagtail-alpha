# Generated by Django 3.2.12 on 2022-05-31 10:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forms", "0002_formfield_clean_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="formfield",
            name="default_value",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="formpage",
            name="from_address",
            field=models.EmailField(blank=True, max_length=255),
        ),
    ]
