# Generated by Django 4.2.14 on 2024-07-16 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topic",
            name="name",
            field=models.CharField(max_length=100),
        ),
    ]