# Generated by Django 4.2.14 on 2024-07-25 15:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("bulletins", "0004_bulletintopicrelationship"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BulletinTopicRelationship",
        ),
    ]
