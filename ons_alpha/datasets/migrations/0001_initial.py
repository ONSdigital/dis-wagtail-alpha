# Generated by Django 4.2.14 on 2024-07-30 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Dataset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("namespace", models.CharField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("version", models.CharField(max_length=255)),
                ("url", models.URLField()),
                ("edition", models.CharField(max_length=255)),
            ],
        ),
        migrations.AddConstraint(
            model_name="dataset",
            constraint=models.UniqueConstraint(fields=("namespace", "edition", "version"), name="dataset_id"),
        ),
    ]
