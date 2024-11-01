# Generated by Django 4.2.16 on 2024-10-31 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charts", "0002_barchart_show_value_labels_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="barchart",
            name="x_type",
            field=models.CharField(default="category", max_length=10),
        ),
        migrations.AddField(
            model_name="linechart",
            name="x_type",
            field=models.CharField(default="category", max_length=10),
        ),
        migrations.AlterField(
            model_name="barchart",
            name="y_type",
            field=models.CharField(default="linear", max_length=10),
        ),
        migrations.AlterField(
            model_name="linechart",
            name="y_type",
            field=models.CharField(default="linear", max_length=10),
        ),
    ]
