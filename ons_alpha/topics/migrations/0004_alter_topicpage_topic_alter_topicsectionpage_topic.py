# Generated by Django 4.2.14 on 2024-08-20 13:49

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taxonomy", "0003_pagetopicrelationship"),
        ("topics", "0003_alter_topicpage_topic_alter_topicsectionpage_topic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topicpage",
            name="topic",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s", to="taxonomy.topic"
            ),
        ),
        migrations.AlterField(
            model_name="topicsectionpage",
            name="topic",
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="%(class)s", to="taxonomy.topic"
            ),
        ),
    ]
