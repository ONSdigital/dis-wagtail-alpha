# Generated by Django 4.2.14 on 2024-09-05 13:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bulletins", "0005_delete_bulletintopicrelationship"),
    ]

    operations = [
        migrations.AddField(
            model_name="bulletinpage",
            name="headline",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
