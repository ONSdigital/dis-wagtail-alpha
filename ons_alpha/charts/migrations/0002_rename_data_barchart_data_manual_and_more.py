# Generated by Django 4.2.16 on 2024-09-30 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charts", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="barchart",
            old_name="data",
            new_name="data_manual",
        ),
        migrations.RenameField(
            model_name="linechart",
            old_name="data",
            new_name="data_manual",
        ),
        migrations.AddField(
            model_name="barchart",
            name="data_source",
            field=models.CharField(default="data_csv", max_length=10),
        ),
        migrations.AddField(
            model_name="linechart",
            name="data_source",
            field=models.CharField(default="data_csv", max_length=10),
        ),
    ]